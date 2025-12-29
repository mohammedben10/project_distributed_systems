from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
import grpc

# Import our forms and models
from .forms import CustomUserCreationForm, UserUpdateForm, ProfileUpdateForm
from .models import History

# --- gRPC IMPORTS (Corrected for new structure) ---
# We use relative imports because these files are now in the 'base' app folder
from . import plant_pb2
from . import plant_pb2_grpc

# --- VIEWS ---

def home(request):
    return render(request, 'base/home.html')

def signup(request):
    if request.method == 'POST':
        # Use CustomUserCreationForm, NOT UserCreationForm
        form = CustomUserCreationForm(request.POST, request.FILES) 
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'base/signup.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("dashbord")
    else:
        form = AuthenticationForm()
    return render(request, 'base/login.html', {"form": form})

def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("home")

@login_required
def dashbord(request):
    image_url = None
    result = None
    
    if request.method == "POST" and request.FILES.get("image"):
        image = request.FILES["image"]
        
        # 1. Save image locally
        fs = FileSystemStorage()
        filename = fs.save(image.name, image)
        image_url = fs.url(filename)
        
        # 2. Prepare image for gRPC (Reset pointer)
        image.seek(0)
        image_bytes = image.read()
        
        # 3. Call gRPC Server
        try:
            # Connect to localhost:50051 (Where server.py is running)
            with grpc.insecure_channel('localhost:50051') as channel:
                stub = plant_pb2_grpc.PlantServiceStub(channel)
                
                # Create Request
                grpc_request = plant_pb2.PlantRequest(image=image_bytes)
                
                # Get Response
                grpc_response = stub.PredictDisease(grpc_request)
                
                # Format result
                confidence_percent = int(grpc_response.confidence * 100)
                result = f"{grpc_response.prediction} ({confidence_percent}%)"
                
        except grpc.RpcError as e:
            result = "Error: AI Server is down or unreachable."
            print(f"gRPC Error: {e}")
        except Exception as e:
            result = f"Error: {str(e)}"

        # 4. Save to History
        History.objects.create(
            user=request.user,
            image=filename,
            result=result
        )

    profile = request.user.profile
    return render(request, 'base/dashbord.html', {
        "result": result, 
        "image_url": image_url, 
        "profile": profile
    })

@login_required
def history(request):
    items = History.objects.filter(user=request.user).order_by('-id') # Newest first
    profile = request.user.profile

    paginator = Paginator(items, 5)
    page = request.GET.get('page')
    items_page = paginator.get_page(page)

    return render(request, "base/history.html", {
        "items": items_page,
        "profile": profile,
    })

@login_required
def delete_history(request, pk):
    item = get_object_or_404(History, id=pk, user=request.user)
    item.delete()
    return redirect("history")

@login_required
def edit_profile(request):
    user = request.user
    profile = user.profile

    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect("dashbord")

    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileUpdateForm(instance=profile)

    return render(
        request,
        "base/edit_profile.html",
        {"user_form": user_form, "profile_form": profile_form}
    )