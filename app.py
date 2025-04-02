from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

# Game state
game_state = {
    "turn": None,  # "player" or "ai"
    "player_score": 0,
    "ai_score": 0,
    "player_batting": None,  # True if player is batting, False if AI is batting
    "first_innings": True,  # Track innings
    "target": None,
    "game_over": False,
    "waiting_for_choice": False  # Track if player needs to choose batting/bowling
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/toss', methods=['POST'])
def toss():
    user_choice = request.json['choice']
    toss_result = random.choice(["heads", "tails"])

    if user_choice == toss_result:
        game_state["waiting_for_choice"] = True  # Player chooses to bat or bowl
        return jsonify({"toss_result": toss_result, "won_toss": True})
    else:
        # AI decides randomly to bat or bowl
        game_state["player_batting"] = random.choice([True, False])
        game_state["turn"] = "player" if not game_state["player_batting"] else "ai"
        return jsonify({"toss_result": toss_result, "won_toss": False, "ai_choice": "bat" if game_state["player_batting"] else "bowl"})

@app.route('/choose', methods=['POST'])
def choose():
    choice = request.json['choice']  # "bat" or "bowl"
    game_state["player_batting"] = (choice == "bat")
    game_state["turn"] = "player" if choice == "bat" else "ai"
    game_state["waiting_for_choice"] = False
    return jsonify({"player_batting": game_state["player_batting"]})

@app.route('/play', methods=['POST'])
def play():
    if game_state["game_over"]:
        return jsonify({"message": "Game over. Refresh to restart."})

    player_choice = request.json['player_choice']
    ai_choice = random.randint(1, 6)
    
    if game_state["player_batting"]:  # Player batting
        if player_choice == ai_choice:
            if game_state["first_innings"]:
                game_state["first_innings"] = False
                game_state["target"] = game_state["player_score"] + 1
                game_state["player_batting"] = False  # AI now bats
                game_state["turn"] = "ai"
                message = f"OUT! You set a target of {game_state['target']} runs. Now AI bats!"
            else:
                game_state["game_over"] = True
                message = f"OUT! AI wins by {game_state['target'] - game_state['player_score']} runs."
        else:
            game_state["player_score"] += player_choice
            message = f"You chose {player_choice}, AI chose {ai_choice}. You scored {player_choice} runs."

            if not game_state["first_innings"] and game_state["player_score"] >= game_state["target"]:
                game_state["game_over"] = True
                message = f"You chased the target! You win by {game_state['player_score'] - game_state['target']} runs!"
    
    else:  # AI batting
        if player_choice == ai_choice:
            if game_state["first_innings"]:
                game_state["first_innings"] = False
                game_state["target"] = game_state["ai_score"] + 1
                game_state["player_batting"] = True  # Player now bats
                game_state["turn"] = "player"
                message = f"OUT! AI set a target of {game_state['target']} runs. Now you bat!"
            else:
                game_state["game_over"] = True
                message = f"OUT! You win by {game_state['target'] - game_state['ai_score']} runs."
        else:
            game_state["ai_score"] += ai_choice
            message = f"You bowled {player_choice}, AI chose {ai_choice}. AI scored {ai_choice} runs."

            if not game_state["first_innings"] and game_state["ai_score"] >= game_state["target"]:
                game_state["game_over"] = True
                message = f"AI chased the target! AI wins by {game_state['ai_score'] - game_state['target']} runs!"
    
    return jsonify({
        "message": message,
        "player_score": game_state["player_score"],
        "ai_score": game_state["ai_score"],
        "turn": game_state["turn"],
        "target": game_state["target"],
        "game_over": game_state["game_over"],
        "ai_choice": ai_choice  # Include AI's choice in the response
    })

if __name__ == '__main__':
    app.run(debug=True)
