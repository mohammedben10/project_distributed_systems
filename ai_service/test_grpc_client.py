import grpc
import plant_pb2
import plant_pb2_grpc
import os

def run():
    # Path to an image to test
    image_path = os.path.join("..", "web_gateway", "media", "potato.png")
    
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        return

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    print(f"Connecting to gRPC server at localhost:50051...")
    try:
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = plant_pb2_grpc.PlantServiceStub(channel)
            request = plant_pb2.PlantRequest(image=image_bytes)
            response = stub.PredictDisease(request)
            print(f"Prediction: {response.prediction}")
            print(f"Confidence: {response.confidence:.2f}")
    except Exception as e:
        print(f"gRPC call failed: {e}")

if __name__ == "__main__":
    run()
