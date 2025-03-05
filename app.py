from flask import Flask, render_template, request, redirect, url_for, session
import csv
import random
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Define 20 different samples, each stored in a separate folder (static/sampleX/)
samples = {
    f"sample_{i}": {
        "full_song": f"static/sample{i}/full_song.wav",
        "parts": {
            "LIME": {
                "spectrogram": f"static/sample{i}/spectrogram_LIME.png",
                "audio_1": f"static/sample{i}/relevant_LIME1.wav",
                "audio_2": f"static/sample{i}/relevant_LIME2.wav",
                "audio_irrelevant": f"static/sample{i}/irrelevant_LIME.wav"
            },
            "SHAP": {
                "spectrogram": f"static/sample{i}/spectrogram_SHAP.png",
                "audio_1": f"static/sample{i}/relevant_SHAP1.wav",
                "audio_2": f"static/sample{i}/relevant_SHAP2.wav",
                "audio_irrelevant": f"static/sample{i}/irrelevant_SHAP.wav"
            },
            "GradCAM": {
                "spectrogram": f"static/sample{i}/spectrogram_GradCAM.png",
                "audio_1": f"static/sample{i}/relevant_GradCAM1.wav",
                "audio_2": f"static/sample{i}/relevant_GradCAM2.wav",
                "audio_irrelevant": f"static/sample{i}/irrelevant_GradCAM.wav"
            }
        }
    }
    for i in range(1, 21)  # Samples 1 to 20
}

@app.route('/', methods=['GET', 'POST'])
def start():
    """Ask for user information before starting the test."""
    if request.method == 'POST':
        session["name"] = request.form["name"].strip()
        session["surname"] = request.form["surname"].strip()
        session["age"] = request.form["age"].strip()
        session["gender"] = request.form["gender"]
        session["samples_completed"] = 0  
        session["sample_order"] = random.sample(list(samples.keys()), 20)  # Random order of 20 samples

        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)

        filename = f"data/{session['name']}_{session['surname']}.csv"
        if not os.path.exists(filename):
            with open(filename, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Sample ID", "Technique", "Audio 1 Rating", "Audio 2 Rating", "Irrelevant Rating"])

        return redirect(url_for('index'))  # Start the test

    return render_template("start.html")

@app.route('/test')
def index():
    """Display the next sample in the random order."""
    if "name" not in session or "surname" not in session:
        return redirect(url_for("start"))  

    if session["samples_completed"] >= 20:
        return redirect(url_for("thank_you"))

    sample_id = session["sample_order"][session["samples_completed"]]
    return render_template("index.html", sample_id=sample_id, sample=samples[sample_id])

@app.route('/submit_ratings', methods=['POST'])
def submit_ratings():
    """Save user ratings and move to the next sample."""
    if "name" not in session or "surname" not in session:
        return redirect(url_for("start"))  

    data = request.json
    filename = f"data/{session['name']}_{session['surname']}.csv"

    with open(filename, "a", newline="") as file:
        writer = csv.writer(file)
        for technique, ratings in data["ratings"].items():
            writer.writerow([data["sample_id"], technique, ratings["audio_1"], ratings["audio_2"], ratings["irrelevant"]])

    # Move to the next sample
    session["samples_completed"] += 1

    if session["samples_completed"] >= 20:
        return {"message": "Test completed! Redirecting to final page...", "completed": True}
    else:
        return {"message": "Ratings recorded! Loading next sample...", "completed": False}

@app.route('/thank_you')
def thank_you():
    """Show the final page after completing 20 samples."""
    return "<h1>Thank you for participating!</h1><p>You have completed the test.</p>"

if __name__ == "__main__":
    app.run(debug=True)


