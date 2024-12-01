var descr_input = document.getElementById('description');

if (descr_input) {
  fetch("http://localhost:5000/add-description/<int:id>")
}