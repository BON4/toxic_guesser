async function postData() {
    const comment = $("#mytextarea").val();
    const response = await fetch("/moderate", {
        method: "POST",
        mode: "cors",
        cache: 'no-cache',
        credentials: "same-origin",
        headers: {
            'Content-Type': 'application/json'
        },
        redirect: 'follow',
        referrerPolicy: 'no-referrer',
        body: JSON.stringify({ comments: [{ "comment_text": comment }] })
    });
    return await response.json();
}

$(document).ready(function () {
    $("#myform").submit(function (event) {
        postData().then((data) => {
            console.log(data[0])
            $("#toxic").html(parseFloat(data[0].toxic).toFixed(2));
            $("#severe_toxic").html(parseFloat(data[0].severe_toxic).toFixed(2));
            $("#obscene").html(parseFloat(data[0].obscene).toFixed(2));
            $("#insult").html(parseFloat(data[0].insult).toFixed(2));
            $("#identity_hate").html(parseFloat(data[0].identity_hate).toFixed(2));
        })
        event.preventDefault();
    });
});