$(document).ready(function() {
    // Load shoes from Flask (passed via Jinja2)
    var database_shoes = JSON.parse('{{ shoes | tojson | safe }}');

    // Map database shoes to category-specific arrays
    let mens_shoes = database_shoes.filter(shoe => shoe.category === "Men's Shoes");
    let womens_shoes = database_shoes.filter(shoe => shoe.category === "Women's Shoes");
    let kids_shoes = database_shoes.filter(shoe => shoe.category === "Kids' Shoes");
    let sports_shoes = database_shoes.filter(shoe => shoe.category === "Sports Shoes");
    let casual_shoes = database_shoes.filter(shoe => shoe.category === "Casual Shoes");

    // Combine all shoes for search and sort functionality
    let all_shoes = [...mens_shoes, ...womens_shoes, ...kids_shoes, ...sports_shoes, ...casual_shoes];

    // Display shoes
    function displayShoes(shoesToDisplay) {
        const shoeList = $('#shoeList');
        shoeList.empty();
        if (shoesToDisplay.length === 0) {
            shoeList.append('<p>No shoes found in this category.</p>');
            return;
        }
        shoesToDisplay.forEach(shoe => {
            const shoeDiv = $('<div>').addClass('shoe-item').attr('data-id', shoe.id);
            shoeDiv.append(`
                <img src="/static/uploads/${shoe.image}" alt="${shoe.name}">
                <h3>${shoe.name}</h3>
                <p><strong>ID:</strong> ${shoe.id}</p>
                <p><strong>Size:</strong> ${shoe.size}</p>
                <p class="price">KSh ${shoe.price}</p>
                <button class="book-btn" data-id="${shoe.id}">Order Now</button>
                <div class="shoe-details">${shoe.details}</div>
            `);
            shoeList.append(shoeDiv);
        });

        // Make entire card clickable to toggle details
        $('.shoe-item').off('click').on('click', function(e) {
            // Prevent toggle if clicking the button
            if (!$(e.target).hasClass('book-btn')) {
                $(this).find('.shoe-details').slideToggle();
            }
        });

        // Order button functionality
        $('.book-btn').off('click').on('click', function(e) {
            e.stopPropagation(); // Prevent card click from toggling details
            const shoeId = $(this).data('id');
            const shoeName = $(this).closest('.shoe-item').find('h3').text();
            $.ajax({
                url: '/order',
                method: 'POST',
                data: { shoe_id: shoeId },
                success: function(response) {
                    if (response.success) {
                        alert(`You have ordered: ${shoeName}`);
                    } else {
                        alert(response.message);
                    }
                },
                error: function() {
                    alert('An error occurred while placing the order.');
                }
            });
        });
    }

    // Initial display
    displayShoes(all_shoes);

    // Sort functionality
    $('#sortSelect').off('change').on('change', function() {
        const sortBy = $(this).val();
        let sortedShoes = [...all_shoes];
        if (sortBy === 'price-low') {
            sortedShoes.sort((a, b) => a.price - b.price);
        } else if (sortBy === 'price-high') {
            sortedShoes.sort((a, b) => b.price - a.price);
        } else if (sortBy === 'popularity') {
            // Placeholder until rating is added; sort by price (high to low) as a fallback
            sortedShoes.sort((a, b) => b.price - a.price);
        }
        displayShoes(sortedShoes);
    });

    // Real-time search with autocomplete
    $("#searchInput").autocomplete({
        source: function(request, response) {
            const term = request.term.toLowerCase();
            const filteredShoes = all_shoes.filter(shoe => 
                shoe.name.toLowerCase().includes(term) ||
                shoe.category.toLowerCase().includes(term) // Allow searching by category too
            );
            response(filteredShoes.map(shoe => shoe.name));
        },
        select: function(event, ui) {
            const selectedShoe = all_shoes.find(shoe => shoe.name === ui.item.value);
            displayShoes([selectedShoe]);
            $(this).val(''); // Clear input after selection
            return false;
        }
    });

    // Search button click
    $('#searchButton').off('click').on('click', function() {
        const query = $('#searchInput').val().toLowerCase();
        const filteredShoes = all_shoes.filter(shoe => 
            shoe.name.toLowerCase().includes(query) ||
            shoe.category.toLowerCase().includes(query)
        );
        displayShoes(filteredShoes);
    });

    // Real-time search as user types
    $('#searchInput').off('input').on('input', function() {
        const query = $(this).val().toLowerCase();
        const filteredShoes = all_shoes.filter(shoe => 
            shoe.name.toLowerCase().includes(query) ||
            shoe.category.toLowerCase().includes(query)
        );
        displayShoes(filteredShoes);
    });

    // Category filter in sidebar
    $('.sidebar li').off('click').on('click', function() {
        const category = $(this).text();
        let shoesToDisplay;
        switch (category) {
            case "Men's Shoes":
                shoesToDisplay = mens_shoes;
                break;
            case "Women's Shoes":
                shoesToDisplay = womens_shoes;
                break;
            case "Kids' Shoes":
                shoesToDisplay = kids_shoes;
                break;
            case "Sports Shoes":
                shoesToDisplay = sports_shoes;
                break;
            case "Casual Shoes":
                shoesToDisplay = casual_shoes;
                break;
            default:
                shoesToDisplay = all_shoes; // Show all if no category matches
        }
        displayShoes(shoesToDisplay);
    });

    // Hamburger menu toggle for small devices
    $('.hamburger').off('click').on('click', function() {
        $('.sidebar, .nav-right').toggleClass('active');
    });
});