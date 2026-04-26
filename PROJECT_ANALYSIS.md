# 🌿 Plant Disease Detection System — Project Analysis

## Overview

This is a **distributed system** for detecting plant diseases from images using AI. The project follows a **client-server microservices architecture**, splitting concerns between a web front-end gateway and a standalone AI inference service that communicate over **gRPC**.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                    User (Browser)                   │
└───────────────────────┬─────────────────────────────┘
                        │  HTTP (Django)
                        ▼
┌───────────────────────────────────────────────────────┐
│               Web Gateway (Django)                    │
│          web_gateway/  —  port: 8000                  │
│  - Auth (login/signup)                                │
│  - Image upload                                       │
│  - History management                                 │
│  - Profile management                                 │
└───────────────────────┬───────────────────────────────┘
                        │  gRPC (port 50051)
                        ▼
┌───────────────────────────────────────────────────────┐
│               AI Service (Python/gRPC)                │
│          ai_service/  —  port: 50051                  │
│  - ResNet-18 model inference                          │
│  - 38-class plant disease classification              │
└───────────────────────────────────────────────────────┘
```

The two services communicate using a **Protocol Buffer** contract defined in `protos/plant.proto`.

---

## 📁 Project Structure

```
ENTREPRO/
├── README.md                        # Minimal project title file
├── protos/
│   └── plant.proto                  # gRPC service contract
├── ai_service/                      # Microservice #1: AI Inference Server
│   ├── server.py                    # gRPC server entry point
│   ├── plant_pb2.py                 # Auto-generated protobuf message classes
│   ├── plant_pb2_grpc.py            # Auto-generated gRPC stubs
│   ├── plant_disease_resnet18.pth   # Trained PyTorch model (~44 MB)
│   ├── requirements.txt             # Python dependencies for AI service
│   ├── model/
│   │   └── Crop_desease_model.ipynb # Jupyter notebook used to train the model
│   └── .gitignore
└── web_gateway/                     # Microservice #2: Django Web Application
    ├── manage.py
    ├── db.sqlite3                   # Local SQLite database
    ├── requirements.txt             # Python dependencies for web gateway
    ├── distributed_system/          # Django project configuration
    │   ├── settings.py
    │   ├── urls.py
    │   ├── asgi.py
    │   └── wsgi.py
    ├── base/                        # Main Django application
    │   ├── models.py                # Profile + History models
    │   ├── views.py                 # All view logic (auth, dashboard, history)
    │   ├── forms.py                 # Registration, update forms
    │   ├── urls.py                  # URL routing
    │   ├── admin.py
    │   ├── plant_pb2.py             # Copy of protobuf generated classes
    │   ├── plant_pb2_grpc.py        # Copy of gRPC stubs
    │   ├── migrations/
    │   │   ├── 0001_initial.py      # Profile model migration
    │   │   └── 0002_history.py      # History model migration
    │   ├── templates/base/
    │   │   ├── base.html            # Base layout template
    │   │   ├── home.html            # Landing page
    │   │   ├── login.html           # Login page
    │   │   ├── signup.html          # Registration page
    │   │   ├── dashbord.html        # Image upload + prediction display
    │   │   ├── history.html         # Prediction history listing
    │   │   └── edit_profile.html    # User profile editor
    │   └── static/
    │       ├── css/style.css        # Global stylesheet
    │       ├── images/              # Static image assets
    │       └── videos/              # Static video assets
    └── media/                       # User-uploaded files (served at runtime)
        ├── avatars/                 # Profile picture uploads
        └── (uploaded plant images)
```

---

## ⚙️ Service 1 — AI Inference Server (`ai_service/`)

### Purpose
A standalone Python gRPC server that loads a pre-trained **ResNet-18** model and performs image classification to detect plant diseases.

### Technology Stack
| Component | Technology |
|-----------|-----------|
| Language | Python |
| ML Framework | PyTorch + TorchVision |
| Communication | gRPC (port **50051**) |
| Image Processing | Pillow (PIL) |
| Concurrency | `ThreadPoolExecutor` (10 workers) |

### How It Works
1. On startup, loads `plant_disease_resnet18.pth` into a ResNet-18 skeleton with a custom final layer (38 output classes).
2. Listens on `[::]:50051` for incoming `PredictDisease` RPC calls.
3. Receives raw image bytes from the Django client.
4. Preprocesses the image: resize to 224×224, normalize to ImageNet stats.
5. Runs inference, applies `softmax` to get probabilities.
6. Returns the class name with the highest probability + confidence score.

### Supported Plant / Disease Classes (38 total)
Covers diseases for: **Apple, Blueberry, Cherry, Corn, Grape, Orange, Peach, Bell Pepper, Potato, Raspberry, Soybean, Squash, Strawberry, Tomato**

### Model Training
- Notebook: `ai_service/model/Crop_desease_model.ipynb`
- Architecture: ResNet-18 (transfer learning, fine-tuned for 38 classes)
- Hardware: Automatically uses CUDA GPU if available, otherwise CPU

---

## ⚙️ Service 2 — Web Gateway (`web_gateway/`)

### Purpose
A **Django** web application serving as the user-facing front-end and the gRPC client that relays image analysis requests to the AI service.

### Technology Stack
| Component | Technology |
|-----------|-----------|
| Language | Python |
| Web Framework | Django |
| Database (local) | SQLite3 |
| Database (cloud) | PostgreSQL via `dj_database_url` (Render-ready) |
| Communication | gRPC client (stub connecting to `localhost:50051`) |
| Auth | Django built-in auth system |

### Database Models

#### `Profile`
Extends Django's built-in `User` with additional fields:
| Field | Type | Description |
|-------|------|-------------|
| `user` | OneToOne → User | Linked Django user |
| `avatar` | ImageField | Profile picture (defaults to `avatars/default.jpg`) |
| `pay` | CharField(50) | Country of the user |
| `ville` | CharField(50) | City of the user |

#### `History`
Stores each prediction made by a user:
| Field | Type | Description |
|-------|------|-------------|
| `user` | ForeignKey → User | Owner of the record |
| `image` | ImageField | Uploaded plant image |
| `result` | TextField | Prediction text + confidence |
| `created_at` | DateTimeField | Auto-set on creation (ordered newest first) |

### URL Routes
| URL | View | Description |
|-----|------|-------------|
| `/` | `home` | Public landing page |
| `/dashbord/` | `dashbord` | Image upload + prediction (login required) |
| `/signup/` | `signup` | User registration |
| `/login/` | `login_view` | User login |
| `/logout/` | `logout_view` | User logout |
| `/edit-profile/` | `edit_profile` | Profile editor (login required) |
| `/history/` | `history` | Paginated prediction history (login required) |
| `/history/delete/<pk>/` | `delete_history` | Delete a history record (login required) |

### Forms
| Form | Purpose |
|------|---------|
| `CustomUserCreationForm` | Extended registration form (username, email, avatar, country, city) |
| `UserUpdateForm` | Edit basic User fields (username, last name, email) |
| `ProfileUpdateForm` | Edit profile fields (avatar, country, city) |

### Templates
| Template | Description |
|----------|-------------|
| `base.html` | Shared layout (navbar, footer, CSS links) |
| `home.html` | Public landing / marketing page |
| `login.html` | Login form |
| `signup.html` | Registration form |
| `dashbord.html` | Main dashboard: image upload, result display |
| `history.html` | Paginated prediction history list |
| `edit_profile.html` | Profile editing form |

---

## 🔗 gRPC Contract (`protos/plant.proto`)

```protobuf
syntax = "proto3";

service PlantService {
  rpc PredictDisease (PlantRequest) returns (PlantResponse);
}

message PlantRequest {
  bytes image = 1;   // raw image bytes from Django
}

message PlantResponse {
  string prediction = 1;   // e.g. "Tomato___Late_blight"
  float  confidence = 2;   // e.g. 0.97
}
```

The generated Python stubs (`plant_pb2.py`, `plant_pb2_grpc.py`) are duplicated into both `ai_service/` and `web_gateway/base/` so each service can run independently.

---

## 🔄 Request Flow (Step by Step)

```
1. User logs in and navigates to /dashbord/
2. User uploads a plant image via the HTML form
3. Django saves the image to /media/ (FileSystemStorage)
4. Django reads the image as raw bytes
5. Django opens a gRPC channel to localhost:50051
6. Django sends a PlantRequest(image=<bytes>) to the AI service
7. AI service receives bytes, opens as PIL Image, applies transforms
8. Model runs inference → softmax → picks top class
9. AI service returns PlantResponse(prediction=..., confidence=...)
10. Django formats: "Tomato___Late_blight (97%)" and saves to History
11. User sees the result + image on the dashboard
```

---

## 🚀 Deployment Considerations

| Aspect | Detail |
|--------|--------|
| **Local Database** | SQLite3 (`db.sqlite3`) — default |
| **Cloud Database** | Auto-switches to PostgreSQL if `DATABASE_URL` env variable is set |
| **Static Files** | `STATIC_ROOT` set for `collectstatic` (Render-compatible) |
| **Allowed Hosts** | `['*']` — open (should be restricted in production) |
| **Debug Mode** | `DEBUG = True` — should be `False` in production |
| **gRPC Host** | Hardcoded to `localhost:50051` — should be configurable via env variable for cloud |

---

## 📦 Dependencies Summary

### AI Service (`ai_service/requirements.txt`)
- `torch`, `torchvision` — Deep learning
- `grpcio`, `grpcio-tools` — gRPC server
- `Pillow` — Image I/O

### Web Gateway (`web_gateway/requirements.txt`)
- `Django` — Web framework
- `grpcio`, `grpcio-tools` — gRPC client
- `Pillow` — Image handling
- `dj_database_url` — Cloud DB URL parsing (Render/Heroku)
- `gunicorn` — Production WSGI server

---

## ⚠️ Known Issues & Improvements

| Issue | Severity | Suggestion |
|-------|----------|------------|
| `DEBUG = True` in production | 🔴 High | Set via env variable |
| Secret key exposed in `settings.py` | 🔴 High | Use `python-decouple` or env variable |
| gRPC address hardcoded to `localhost:50051` | 🟡 Medium | Read from env variable for cloud deployment |
| `ALLOWED_HOSTS = ['*']` | 🟡 Medium | Restrict to actual domain |
| Typo: `dashbord` (should be `dashboard`) | 🟢 Low | Consistent naming |
| Duplicate generated protobuf files | 🟢 Low | Use a shared package or path |
