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

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function sendAndReceiveData() {
    let urlTo = '/replay-game-data/'.concat(id)
    console.log(urlTo)
    fetch(urlTo, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        },
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            let delay = 1000; // Start with a second delay
            let turn = 0

            for (let i = 0; i < data.board_steps.length; i++) {
                let buttonIndex = data.board_steps[i]
                
                    setTimeout(() => {
                        allButtons[buttonIndex].innerText = data.sing_order[turn];
                        turn = (turn + 1) % 2
                        console.log(buttonIndex); }, delay);

                    delay += 1000; // Increase the delay by second each time
            }
            if (data.winner != "DRAW") {
            
            setTimeout(() => {
                for (let block of data.win_board_location) {
                    allButtons[block].style.setProperty("background", '#0dcaf0');
                    allButtons[block].style.setProperty("color", 'black');};}, 1000 * data.board_steps.length);}
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
}

sendAndReceiveData()