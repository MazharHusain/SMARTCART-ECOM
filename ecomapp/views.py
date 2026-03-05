from django.shortcuts import render,HttpResponse,redirect
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from .models import Product,Contact,Orders,OrderUpdate
from math import ceil
import json
import razorpay
from django.views.decorators.csrf import csrf_exempt

def home(request):
    current_user = request.user
    print(current_user)
    allProds = []
    catprods = Product.objects.values('category','id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod= Product.objects.filter(category=cat)
        n=len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])
    params= {'allProds':allProds}
    return render(request,'index.html',params)

def about(request):
    return render(request, 'about.html')

def contactus(request):
    if not request.user.is_authenticated:
        messages.warning(request,"Login & Try Again")
        return redirect('/login')
    if request.method=="POST":
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        desc = request.POST.get('desc', '')
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        messages.success(request,"Contact Form is Submitted")
    return render(request, 'contactus.html')

def tracker(request):
    if not request.user.is_authenticated:
        messages.warning(request,"Login & Try Again")
        return redirect('/login')
    if request.method=="POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Orders.objects.filter(order_id=orderId, email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps([updates, order[0].items_json], default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{}')
        except Exception as e:
            return HttpResponse('{}')

    return render(request, 'tracker.html')

def productView(request, myid):
    product = Product.objects.filter(id=myid)
    return render(request, 'prodView.html', {'product':product[0]})

def handlelogin(request):
      if request.method == 'POST':
        loginusername=request.POST['email']
        loginpassword=request.POST['pass1']
        user=authenticate(username=loginusername,password=loginpassword)
       
        if user is not None:
            login(request,user)
            messages.info(request,"Successfully Logged In")
            return redirect('/')

        else:
            messages.error(request,"Invalid Credentials")
            return redirect('/login')    
      return render(request,'login.html')         

def signup(request):
    if request.method == 'POST':
        email=request.POST.get('email')
        pass1=request.POST.get('pass1')
        pass2=request.POST.get('pass2')
        if pass1 != pass2:

            messages.error(request,"Password do not Match,Please Try Again!")
            return redirect('/signup')
        try:
            if User.objects.get(username=email):
                messages.warning(request,"Email Already Exists")
                return redirect('/signup')
        except Exception as identifier:            
            pass 
        try:
            if User.objects.get(email=email):
                messages.warning(request,"Email Already Exists")
                return redirect('/signup')
        except Exception as identifier:
            pass        
        user=User.objects.create_user(email,email,pass1)
        user.save()
        messages.info(request,'Thanks For Signing Up')
        return redirect('/login')    
    return render(request,"signup.html")        

def logouts(request):
    logout(request)
    messages.warning(request,"Logout Success")
    return render(request,'login.html')

def request_reset_email(request):

    if request.method == 'POST':

        email = request.POST.get("email")

        if User.objects.filter(email=email).exists():

            subject = "Password Reset Requested"

            email=request.POST.get("email")

            message = "Click the link below to reset your password"

            from_email = settings.EMAIL_HOST_USER

            recipient_list = [email]
            send_mail(subject, message, from_email, recipient_list)
            messages.success(request,"Password Reset Email Sent")

        else:
            messages.error(request,"Email Not Found")
    return render(request,"request-reset-email.html")

def set_new_password(request, uidb64, token):
    return render(request, 'set-new-password.html')

client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def checkout(request):

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        items_json = request.POST.get("itemsJson")
        import json
        items = json.loads(items_json)
        total = 0
        for item in items:
            product_id = int(item.replace('pr',''))
            product = Product.objects.get(id=product_id)
            qty = items[item][0]
            total += product.price * qty
        amount = total * 100
        order = Orders.objects.create(
            name=name,
            email=email,
            items_json=items_json,
            amount=total,
            status="Pending"
        )
        razorpay_order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": 1
        })
        order.razorpay_order_id = razorpay_order['id']
        order.save()
        context = {
            "order_id": razorpay_order['id'],
            "amount": amount,
            "key": settings.RAZORPAY_KEY_ID,
            "name": name,
            "email": email
        }
        return render(request, "payment.html", context)
    return render(request, "checkout.html")

@csrf_exempt

def payment_success(request):
    payment_id = request.GET.get("payment_id")
    order_id = request.GET.get("order_id")
    try:
        order = Orders.objects.get(razorpay_order_id=order_id)
        order.payment_id = payment_id
        order.status = "Paid"
        order.save()
        return render(request,"paymentstatus.html",{
            "status":"Payment Successful",
            "order_id":order_id,
            "payment_id":payment_id
        })

    except:
        return render(request,"paymentstatus.html",
        {
            "status":"Payment Failed"
        })

