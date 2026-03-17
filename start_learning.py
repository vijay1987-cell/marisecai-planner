import torch

# 1. Create a "Tensor" (AI's version of a number) on the CPU
cpu_data = torch.tensor([10.0, 20.0, 30.0])
print(f"Data location: {cpu_data.device} (Slow)")

# 2. Teleport the data to the GPU (CUDA)
gpu_data = cpu_data.to("cuda")

# 3. Check where it is now
print(f"Data location: {gpu_data.device} (Fast!)")

# 4. Do math on the GPU
result = gpu_data * 2
print(f"GPU Math Result: {result}")