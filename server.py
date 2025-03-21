def forward(content):
    file1 = open("output.txt", "a")  # append mode
    file1.write(content.decode("utf-8"))
    file1.close()