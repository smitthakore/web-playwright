# run with python src.agent.test_browser_flow.py
from .agent import PlaywrightAgent

if __name__ == "__main__":
    print("\n" + "="*80)
    print("TEST: Browser Flow (Navigate -> Click -> Generate)")
    print("="*80 + "\n")
    
    agent = PlaywrightAgent()
    
    # Complex prompt requiring tool use
    prompt = "Navigate to https://example.com, click the 'More information' link, and generate a Playwright script for this flow."
    
    print(f"Prompt: {prompt}\n")
    
    result = agent.process_request(prompt)
    
    if result["success"]:
        print("\n" + "="*80)
        print("✅ TEST PASSED")
        print("="*80)
        print(f"Task Type: {result['task_type']}")
        print(f"Graph Steps: {result['graph_steps']}")
        print(f"Duration: {result['duration']:.2f}s")
        print(f"\nGenerated Code:\n{result['generated_code'][:500]}...")
    else:
        print("\n" + "="*80)
        print("❌ TEST FAILED")
        print("="*80)
        print(f"Error: {result['error']}")
        print(f"Response: {result['response']}")
