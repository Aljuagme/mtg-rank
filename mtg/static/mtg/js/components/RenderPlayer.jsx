const RenderPlayer = ({ selectedPlayer, setSelectedDeck, loggedInUserId }) => {
    const [player, setPlayer] = React.useState(null);
    const [decksPlayer, setDecksPlayer] = React.useState([]);
    const [showForm, setShowForm] = React.useState(false);
    const [category, setCategory] = React.useState([]);

    const playerId = selectedPlayer && selectedPlayer.id;
    const isCurrentUser = loggedInUserId === playerId;
    console.log(`PLAYER ID: ${playerId}`)

    React.useEffect(() => {
        if (playerId) {
            const url = `/get_decks/${parseInt(playerId)}`;

            fetch(url)
                .then(response => {
                    if (!response.ok) {
                        throw new Error("Network response was not ok");
                    }
                    return response.json();
                })
                .then(data => {
                    console.log(data);
                    setPlayer(data["user"]);
                    setDecksPlayer(data["decks"])
                    setSelectedDeck(null)
                })
                .catch(error => console.error(`There was a problem while fetching deck with ID: ${playerId}`, error));
        }
    }, [playerId]); // Only re-run the effect if deckId changes

    if (!player) {
        return <div>No data available for this deck.</div>;
    }

    const handleDeckClick = (deckId) => {
        console.log(deckId);
        setSelectedDeck({ id: deckId });
    };

    // Function to get CSRF token from cookies
    function getCSRFToken() {
        const cookies = document.cookie.split("; ");
        for (let cookie of cookies) {
            if (cookie.startsWith("csrftoken=")) {
                return cookie.split("=")[1];
            }
        }
        return "";
    }

    // Fetch deck options and match results on form open
    const fetchOptions = async () => {
        try {
            const response = await fetch("/get_options/deck");
            const data = await response.json();
            console.log(data)
            setCategory(data["category"]);
        } catch (error) {
            console.error("Error fetching options:", error);
        }
    };

    const handleAddClick = () => {
        setShowForm(true);
        fetchOptions();
    }

    const handleSubmitForm = (event) => {
        event.preventDefault();
        const formData = new FormData(event.target);

        fetch("/add_deck", {
            method: "POST",
            body: formData,
            headers: {
                "X-CSRFToken": getCSRFToken(),
            }
        }).then(response => {
            if (response.ok) {
                setShowForm(false);
                window.location.reload()
            } else {
                console.error("Failed to add Deck");
            }
        });
    }

    return (
        <div>
            <h1>{player.username}. Win Ratio: {player.win_ratio}%</h1>
            <div className="results-page-container">
                <div className="results-table">
                    <table className="table">
                        <thead className="table-light, table-results">
                            <tr>
                                <th scope="col">#</th>
                                <th scope="col">Deck</th>
                                <th scope="col">Category</th>
                                <th scope="col">Total Matches</th>
                                <th scope="col">Victories</th>
                                <th scope="col">Defeats</th>
                                <th scope="col">Draws</th>
                                <th scope="col">Win Ratio</th>
                            </tr>
                        </thead>
                        <tbody className="table-group-divider">
                        {decksPlayer && decksPlayer.length > 0 ? (
                            decksPlayer.map((deck, index) => (
                            <tr key={deck.id}>
                                <th scope="row">{index + 1}</th>
                                <td className="clickable" onClick={() => handleDeckClick(deck.id)}>{deck.name}</td>
                                <td>{deck.category}</td>
                                <td>{deck.total_matches}</td>
                                <td>{deck.wins}</td>
                                <td>{deck.losses}</td>
                                <td>{deck.draws}</td>
                                <td>{deck.win_ratio}%</td>
                            </tr>
                        ))

                        ) : (
                            <tr>
                                <td colSpan="8">No decks available for this player.</td>
                            </tr>
                        )}
                      {isCurrentUser && (
                            <tr>
                                <td>
                                    <button className="button-add" onClick={handleAddClick}>
                                        <img src="/static/mtg/img/add-button.png" alt="Add Deck" />
                                    </button>
                                </td>
                            </tr>
                        )
                        }

                        </tbody>
                    </table>
                </div>

                {/* Form to add new Deck */}
                {showForm &&  (
                    <form onSubmit={handleSubmitForm} className="add-match-form">
                        <h3>Add New Deck</h3>
                        <div>
                            <label>Name: </label>
                            <input name="name"/>
                        </div>
                        <div>
                            <label>Category: </label>
                            <select name="category">
                                {category.length > 0 ? (
                                    category.map(c => (
                                    <option key={c.id} value={c.id}>{c.label}</option>
                                ))
                                ) : (
                                    <option disabled>Loading categories... </option>
                                )
                                }
                            </select>
                        </div>
                        <button type="submit">Submit</button>
                        <button type="button" onClick={() => setShowForm(false)}>Cancel</button>
                    </form>
                )}
            </div>
        </div>
    );
};
