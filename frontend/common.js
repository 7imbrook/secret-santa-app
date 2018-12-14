function status(response) {
    if (response.status >= 200 && response.status < 300) {
        return Promise.resolve(response)
    } else {
        return response.json().then(err => {
            return Promise.reject(new Error(err.message))
        })
    }
}

function json(response) {
    return response.json()
}

function submitPhoneNumber() {
    $("#error_display").html("").hide();
    $("#number_input").attr("disabled", "disabled");
    $("#register_number").attr("disabled", "disabled");

    const number = document.getElementById("number_input").value
    const csrfmiddlewaretoken = document.querySelector("input[name='csrfmiddlewaretoken']").value
    fetch("/api/register", {
        method: 'post',
        headers: {
            'X-CSRFToken': csrfmiddlewaretoken,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            number
        })
    })
        .then((r) => {
            return r
        })
        .then(status)
        .then(json)
        .then(data => {
            if (data.code) {
                $("#code_display").html(data.code)
                $("#code_display_block").show()
            } else {
                $("#already_registered").show()
            }
        })
        .catch(err => {
            console.log(err)
            $("#error_display").html(err).show();
            $("#register_number").removeAttr("disabled");                             
            $("#number_input").removeAttr("disabled");                             
        })
}

$(document).ready(function () {
    $("#register_number").click(submitPhoneNumber);
    var clipboard = new ClipboardJS('.btn');

    // clipboard.on('success', function(e) {
    //     console.info('Action:', e.action);
    //     console.info('Text:', e.text);
    //     console.info('Trigger:', e.trigger);

    //     e.clearSelection();
    // });

    // clipboard.on('error', function(e) {
    //     console.error('Action:', e.action);
    //     console.error('Trigger:', e.trigger);
    // });
});


