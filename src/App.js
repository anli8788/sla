import { useEffect, useState } from "react";
import "./App.css";
import SLA from "./SLA";

function App() {
  const [data, setData] = useState([
    { name: "SLA1", slaTime: 600, status: false },
    { name: "SLA2", slaTime: 1200, status: false },
    { name: "SLA3", slaTime: 310, status: false },
  ]);

  const [startTime, setStartTime] = useState(0);
  const [status, setStatus] = useState(false);

  const countTime = () => {
    setStartTime(startTime + 1);
  };

  const [hour, setHour] = useState(0);
  const [minite, setMinute] = useState(0);
  const [second, setSecond] = useState(0);
  const [run, setRun] = useState(false);

  function secondsToHms(d) {
    d = Number(d);
    var h = Math.floor(d / 3600);
    var m = Math.floor((d % 3600) / 60);
    var s = Math.floor((d % 3600) % 60);

    var hDisplay = h > 0 ? h + (h === 1 ? "" : "") : "00";
    var mDisplay = m > 0 ? m + (m === 1 ? "" : "") : "00";
    var sDisplay = s > 0 ? s + (s === 1 ? "" : "") : "00";
    setHour(hDisplay);
    setMinute(mDisplay);
    setSecond(sDisplay);
    return hDisplay + mDisplay + sDisplay;
  }

  useEffect(() => {
    if (status === true) {
      if (startTime > 0) {
        if (!startTime) return;

        // save intervalId to clear the interval when the
        // component re-renders
        const intervalId = setInterval(() => {
          setStartTime(startTime + 1);
        }, 1000);
        // clear interval on re-render to avoid memory leaks
        secondsToHms(startTime);
        return () => clearInterval(intervalId);
        // add timeLeft as a dependency to re-rerun the effect
        // when we update it
      }
    }
  }, [startTime, status]);

  useEffect(() => {
    let count = 0;
    data.map((item, idx) => {
      if (item.status === true) {
        count = count + 1;
      }
    });
    if (data.length === count) {
      setStatus(false);
    }
  }, [data]);

  return (
    <div className="App">
      <h1>SLA Demo</h1>
      <div>
        <button
          onClick={() => {
            countTime();
            setRun(true);
            setStatus(true);
          }}
        >
          Start
        </button>
        <div>
          {hour}:{minite}:{second}
        </div>
        <div
          className="row"
          style={{
            display: "flex",
            justifyContent: "space-between",
            marginTop: "2rem",
          }}
        >
          {data.map((item, idx) => {
            return (
              <SLA
                item={item}
                startTime={startTime}
                setStartTime={setStartTime}
                hour={hour}
                minite={minite}
                second={second}
                slaTime={item.slaTime}
                status={status}
                setRun={setRun}
                run={run}
                data={data}
                index={idx}
                setData={setData}
              />
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default App;
