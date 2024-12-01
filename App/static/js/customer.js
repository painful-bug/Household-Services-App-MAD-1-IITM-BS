//VARIABLE DECLARATION AND INITIALISATION
var card_container = document.getElementById("card-container")
var search_bar = document.getElementById("search-bar")
var book_button = document.getElementById("book-service-button")


// BOOK SERVICE FEATURE
// book_button.addEventListener('click', (e) => {
//   e.preventDefault();
//   const url = `http://localhost:5000/services/search/`;
// })




// LIVE DATA SEARCH
const searchDB = async (query) => {
  console.log("SEARCHDB")
  try {

    card_container.innerHTML = '';

    let url = '';

    if (query.length != 0) {
      url = `http://localhost:5000/services/search/${query}`;  // Use relative URL
    } else {
      url = "http://localhost:5000/services/search/";  // Use relative URL
    }
    console.log("URL : ", url);
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const service_list = await response.json();
    console.log("LIST : ", service_list);
    service_list.forEach(service => {
      console.log("SERVICE : ", service);
      const card_ = document.createElement('div');
      card_.classList.add("col");
      card_.classList.add("mb-2");
      card_.innerHTML = `
                        <div class="card" style="max-width: 350px;">
                            <div class="card-body">
                        
                                <h5 class="card-title">${service.name}</h5>
                                <p class="card-text">${service.description}</p>
                                <p class="card-text">
                                    <small class="text-muted">
                                        Base Price: $${service.base_price}<br>
                                        Time Required: ${service.time_required}
                                    </small>
                                </p>
                    
                              <form action='/service-requests/select/${service.id}' method="post">
                                <p name="service-id" style="display: none;">${service.id}</p>
                                <p name="user-id" style="display: none;">${service.user_id}</p>
                                <button type="submit" class="btn btn-outline-success">Book Service</button>
                              </form>
                                </div>
                        </div>
                    `;
      card_container.appendChild(card_);
    });
  } catch (error) {
    console.error("Error fetching search results:", error);
    card_container.innerHTML = '<div class="alert alert-danger">Error loading services</div>';
  }
}

// Debounce the search to prevent too many requests
let timeoutId;
search_bar.addEventListener('keyup', (e) => {
  e.preventDefault()
  clearTimeout(timeoutId);
  timeoutId = setTimeout(() => {
    const content = search_bar.value;
    console.log("CONTENT : ", content);
    console.log("CONTENT LENGTH: ", content.length);

    searchDB(content);

  }, 300);  // Wait 300ms after user stops typing
});
