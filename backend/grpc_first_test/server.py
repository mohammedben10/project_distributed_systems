import io
import grpc
import torch
import torchvision
from concurrent import futures
from PIL import Image
from torchvision import transforms
import plant_pb2
import plant_pb2_grpc

#katshuf wash 3ndk gpu cuda(nvidia) hit models kaytrunaw faster fiha ila la sir l cpu
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

MODEL_PATH = "plant_disease_resnet18.pth"
#class names b mn A l Z hit model kaybdl tritb b alphabet
CLASS_NAMES = [
    'Apple___Apple_scab', 
    'Apple___Black_rot', 
    'Apple___Cedar_apple_rust', 
    'Apple___healthy', 
    'Blueberry___healthy', 
    'Cherry_(including_sour)___Powdery_mildew', 
    'Cherry_(including_sour)___healthy', 
    'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot', 
    'Corn_(maize)___Common_rust_', 
    'Corn_(maize)___Northern_Leaf_Blight', 
    'Corn_(maize)___healthy', 
    'Grape___Black_rot', 
    'Grape___Esca_(Black_Measles)', 
    'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)', 
    'Grape___healthy', 
    'Orange___Haunglongbing_(Citrus_greening)', 
    'Peach___Bacterial_spot', 
    'Peach___healthy', 
    'Pepper,_bell___Bacterial_spot', 
    'Pepper,_bell___healthy', 
    'Potato___Early_blight', 
    'Potato___Late_blight', 
    'Potato___healthy', 
    'Raspberry___healthy', 
    'Soybean___healthy', 
    'Squash___Powdery_mildew', 
    'Strawberry___Leaf_scorch', 
    'Strawberry___healthy', 
    'Tomato___Bacterial_spot', 
    'Tomato___Early_blight', 
    'Tomato___Late_blight', 
    'Tomato___Leaf_Mold', 
    'Tomato___Septoria_leaf_spot', 
    'Tomato___Spider_mites Two-spotted_spider_mite', 
    'Tomato___Target_Spot', 
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus', 
    'Tomato___Tomato_mosaic_virus', 
    'Tomato___healthy'
]
# --- LOAD MODEL ---
def load_model():
    print(f"🚀 Loading model on {DEVICE}...")
    #hna kangado skeleton or body d model
    model = torchvision.models.resnet18(weights=None)
    #hna db had resnet recognize bzaf d lhwayj(dogs,cats....) kandiro hadi bash redoh kaydiha ha f dok 38 diseases dialna
    model.fc = torch.nn.Linear(model.fc.in_features, len(CLASS_NAMES))
    #hna katlo7 dak model li gadina f dak lbody b7ala glti katlo7 brain 
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    #hadi katbdl model mn learning l testing
    return model.to(DEVICE).eval()

model = load_model()

# hna ha katgad image kima model kan kayshufha fash traina
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# --- GRPC SERVICE ---
class PlantService(plant_pb2_grpc.PlantServiceServicer):
    def PredictDisease(self, request, context):
        try:
            #django kaysift tswira bytes walakin image library kaytsna file
            #haka lash bytes.IO kadir l3ba dial trd had bytes b7ala physical file f disk
            image = Image.open(io.BytesIO(request.image)).convert("RGB")
            #hna ai models kaytsnaw batches of images(32 ula ma3rt) walakin 7na endna whda 
            #dik unsqueeze hya l7el bash redoh 9abl image whda
            input_tensor = transform(image).unsqueeze(0).to(DEVICE)
            
            #hna we tell pytorch rah 7na makant3lmosh db mais kantestiw matcalculi walo
            #dik softmax katbdl output d model l probabilites(70%,20%,10%)=100%
            with torch.no_grad():
                output = model(input_tensor)
                probabilities = torch.nn.functional.softmax(output[0], dim=0)
            #hna kanjbdo akbar probability ou index dialha bash nsifto proba ou index il9a classname
            #ou nsiftohom l django
            confidence, index = torch.max(probabilities, 0)
            return plant_pb2.PlantResponse(
                prediction=CLASS_NAMES[index.item()], 
                confidence=confidence.item()
            )
        except Exception as e:
            print(f"❌ Error: {e}")
            return plant_pb2.PlantResponse(prediction="Error", confidence=0.0)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    plant_pb2_grpc.add_PlantServiceServicer_to_server(PlantService(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("🚀 gRPC Server listening on port 50051")
    server.wait_for_termination()



if __name__ == "__main__":
    serve()