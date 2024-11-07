function App() {
    const [roundNumber, setRoundNumber] = React.useState(1);

    // const [players, setPlayers] = React.useState([]);


    return (
        <div>
            <RenderRound
                roundNumber={roundNumber}
                setRoundNumber={setRoundNumber}
            />
        </div>
    )


}