function api(params) {
    return (
        fetch(
            '../api.php', {
                method: 'POST',
                credentials: 'include',
                body: new URLSearchParams(params),
            }
        )
        .then(response => {
            return response.text();
        })
        .then(response => {
            return JSON.parse(response);
        })
    );
}

function setup(pageFName) {
    window.onload = function() {
        api([
            ['submit', 'read'],
            ['page_fname', pageFName],
        ])
        .then(function(json) {
            if (json['errorMessage'] !== null) {
                throw json['errorMessage'];
            }
            let data = json['response'];
            for (let i = 0; i < data.length; i++) {
                let boxX = data[i]['box_x'];
                let boxY = data[i]['box_y'];
                let transcription = data[i]['transcription'];
                let language = data[i]['language'];
                document.getElementById('lang_'+boxX+'_'+boxY).value = language;
                document.getElementById('tran_'+boxX+'_'+boxY).value = transcription;
                document.getElementById('save_'+boxX+'_'+boxY).onclick = function() {
                    api([
                        ['submit', 'update'],
                        ['page_fname', pageFName],
                        ['box_x', boxX],
                        ['box_y', boxY],
                        ['transcription', document.getElementById('tran_'+boxX+'_'+boxY).value],
                        ['language', document.getElementById('lang_'+boxX+'_'+boxY).value],
                    ])
                    .then(function(json) {
                        if (json['errorMessage'] !== null) {
                            throw json['errorMessage'];
                        }
                        else {
                            alert('Saved!')
                        }
                    });
                };
            }
        })
        .catch(function(error) {
            alert(error.toString());
        });
    };
}
