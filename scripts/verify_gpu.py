import tensorflow as tf
import sys

def verify_gpu_setup():
    print("Python Version:", sys.version)
    print("TensorFlow Version:", tf.__version__)
    print("CUDA Available:", tf.test.is_built_with_cuda())
    print("GPU Available:", tf.test.is_built_with_gpu_support())
    print("GPU Devices:", tf.config.list_physical_devices('GPU'))
    
    if tf.test.is_built_with_cuda():
        print("\nCUDA Version:", tf.sysconfig.get_build_info()['cuda_version'])
        print("cuDNN Version:", tf.sysconfig.get_build_info()['cudnn_version'])
    else:
        print("\nCUDA is not available. Please check your installation.")

if __name__ == "__main__":
    verify_gpu_setup() 