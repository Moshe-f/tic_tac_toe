const allButtons = [document.getElementById('button0'),
document.getElementById('button1'),
document.getElementById('button2'),
document.getElementById('button3'),
document.getElementById('button4'),
document.getElementById('button5'),
document.getElementById('button6'),
document.getElementById('button7'),
document.getElementById('button8'),
]

document.addEventListener('DOMContentLoaded', function () {
    for (let element of allButtons) {
        element.addEventListener('click', function () {
            const location = element.value;
            sendAndReceiveData(location)
        });
    }
});

function disabledButtons() {
    for (let button of allButtons) {
        button.disabled = true;
    }
}

function sendAndReceiveData(location) {
    fetch('/move', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ location: location })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            updateTurn(data)
            
            for (let id = 0; id < data.game_board.length; id++) {
                allButtons[id].innerText = data.game_board[id];
            }
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
}

function updateTurn(data) {
    if (data.win === "DRAW") {
        document.getElementById('turn').innerText = "DRAW!"
        disabledButtons()
    } else if (data.win === "") {
        document.getElementById('turn').innerText = data.turn + " turn"
    } else {
        document.getElementById('turn').innerText = data.win + " is the WINNER!"
        for (let block of data.win_board_location) {
            allButtons[block].style.setProperty("background", '#0dcaf0');
            allButtons[block].style.setProperty("color", 'black');
        }
        disabledButtons()
    }
}

document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('restart').addEventListener('click', function () {
        const location = document.getElementById('restart').value;
        sendAndReceiveData(location)
        enabledButtons()
    });
});

function enabledButtons() {
    for (let button of allButtons) {
        button.disabled = false;
        button.style.removeProperty("background");
        button.style.removeProperty("color");
    }
}
