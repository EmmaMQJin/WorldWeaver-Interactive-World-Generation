function submitDescription() {
    const description = document.getElementById("gameDescription").value;
    fetch('/submit-description', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ description: description })
    })
    .then(response => {
        if (response.ok) {
            window.location.href = "/character-description"; // Redirect on success
        } else {
            throw new Error('Submission failed');
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        alert("An error occurred while submitting the description.");
    });
}

function handleClick(itemName) {
    alert('You clicked on ' + itemName);
}
