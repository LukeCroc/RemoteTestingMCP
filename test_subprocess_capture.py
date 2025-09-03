import subprocess
import os

def test_subprocess_capture():
    """测试subprocess capture_output参数对git push的影响"""
    print("=== 测试subprocess capture_output参数的影响 ===")
    
    # 先创建一个测试提交
    with open("test_file.txt", "w") as f:
        f.write("test content")
    
    subprocess.run("git add test_file.txt", shell=True, check=True)
    subprocess.run('git commit -m "Test commit for capture test"', shell=True, check=True)
    
    print("\n1. 测试不使用capture_output (应该能看到认证提示):")
    try:
        result = subprocess.run("git push origin main", shell=True, check=True)
        print(f"退出码: {result.returncode}")
    except subprocess.CalledProcessError as e:
        print(f"失败: {e}")
    
    print("\n2. 测试使用capture_output=True (可能静默失败):")
    try:
        result = subprocess.run("git push origin main", shell=True, check=True, capture_output=True, text=True)
        print(f"退出码: {result.returncode}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"失败: {e}")
        print(f"stderr: {e.stderr}")
        print(f"stdout: {e.stdout}")

if __name__ == "__main__":
    test_subprocess_capture()