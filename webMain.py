from flask import Flask, render_template, request,jsonify

app = Flask(__name__,template_folder="assets/views/",static_folder="assets/lib/")

@app.route('/')
def app_home():
    return render_template("index.html")

# @app.route('/message', methods=['GET','POST'])
# def message():
#     if request.method == "POST":
#         data = request.get_json()
#         chat = data["message"]
#         # print(complete_prompt(chat))

#     return complete_prompt(chat)

app.run(debug=True,port=8081)