Capabilities

1. [x] Version control
2. [x] Virtual environment
3. [x] Machine learning
4. [x] Docker
5. [x] Testing
6. [x] Data engineering, i.e. try making private posts
[ ] Security
[ ] CI/CD pipeline


I. Without Docker:
>> export set FLASK_APP=webapp

(While in HELLOFLASK folder)
(first time)
>> python3 -m flask --app hello_app init-db
(Debug mode) 
>> python3 -m flask --app hello_app run --debug



II. With Docker:
Navigate to the file that contains your app's startup code, and set a breakpoint.
Navigate to Run and Debug and select Docker: Python - General, Docker: Python - Django, or Docker: Python - Flask, as appropriate.
Start debugging using the F5 key.
#     The Docker image builds.
#     The Docker container runs.
The python debugger stops at the breakpoint. Step over this line once.
When ready, press continue.
# The Docker extension will launch your browser to a randomly mapped port

# Runing using flask command in debug:
# Note: do not use app.run() on production server
Debug mode shows an interactive debugger whenever a page raises an exception, and restarts the server whenever you make changes to the code. You can leave it running and just reload the browser page as you follow the tutorial. 
Should be in the top-level flask-tutorial directory, not the hello_app package
>> python3 -m flask --app hello_app run --debug

