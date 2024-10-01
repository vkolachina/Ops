# custom_transformers.rb

# Example custom transformer for a build step
transform "custom_step" do |item|
    {
      name: "Custom Step",
      uses: "actions/custom-action@v1",
      with: {
        param1: item["input1"],
        param2: item["input2"]
      }
    }
  end
  
  # Example custom transformer for a runner
  runner "linux", "ubuntu-latest"