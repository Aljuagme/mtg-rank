function App() {
    const [round, setRound] = React.useState("Round1");
    const [players, setPlayers] = React.useState([]);

    React.useEffect(() => {
        fetch("/tournament/get_players")
        .then(response => {
            if (!response.ok) {
                throw new Error("Error while fetching players");
            }
            return response.json();
        })
        .then(data =>
        {
            console.log("App_data: " + data)
            setPlayers(data)
        })
        .catch(error => console.error("Error fetching players", error));
    }, []);

    console.log(players)

    return (
        <div>
            <RenderRound1 players={players} />
        </div>
    )


}