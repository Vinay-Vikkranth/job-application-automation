"""
Simple test to verify Gradio is working
"""
import gradio as gr

def greet(name):
    return f"Hello {name}!"

# Create a simple interface
demo = gr.Interface(fn=greet, inputs="text", outputs="text")

if __name__ == "__main__":
    print("🚀 Starting simple Gradio test...")
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False)
