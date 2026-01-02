# run with python src.agent.unit_test.py
from agent import PlaywrightAgent

if __name__ == "__main__":
    agent = PlaywrightAgent()
    
    print("\n" + "="*80)
    print("TEST: Generate Login Page POM")
    print("="*80 + "\n")
    
    result = agent.process_request(
        "Generate a Page Object Model for a login page with username, password, and login button"
    )
    
    if result["success"]:
        print("\n" + "="*80)
        print("✅ TEST PASSED")
        print("="*80)
        print(f"Task Type: {result['task_type']}")
        print(f"Class Name: {result['class_name']}")
        print(f"Duration: {result['duration']:.2f}s")
        print(f"Graph Steps: {result['graph_steps']}")
        print(f"\nGenerated Code Length: {len(result['generated_code'])} chars")
    else:
        print("\n" + "="*80)
        print("❌ TEST FAILED")
        print("="*80)
        print(f"Error: {result['error']}")