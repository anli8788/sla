import React, { useEffect, useState } from "react";

const SLA = (props) => {
  const { item, slaTime, status, data, index, setData } = props;

  const [result1, setResult1] = useState("");
  const [result2, setResult2] = useState("");

  //
  const [hourSLA, setHourSLA] = useState("0");
  const [miniteSLA, setMinuteSLA] = useState("0");
  const [secondSLA, setSecondSLA] = useState("0");

  //
  const [hour, setHour] = useState("0");
  const [minite, setMinute] = useState("0");
  const [second, setSecond] = useState("0");

  //
  const [run, setRun] = useState(false);

  const [timeLeft, setTimeLeft] = useState(slaTime);

  const [startTime, setStartTime] = useState(0);
  const [minus, setMinus] = useState("");

  useEffect(() => {
    if (status === true) {
      if (run === false) {
        // if (!timeLeft) return;
        if (timeLeft > 0 && timeLeft <= 300) {
          setResult2("Escalated");
        }
        // save intervalId to clear the interval when the
        // component re-renders
        const intervalId = setInterval(() => {
          setTimeLeft(timeLeft - 1);
        }, 1000);
        // clear interval on re-render to avoid memory leaks
        secondsToHmsSLA(timeLeft);
        return () => clearInterval(intervalId);
        // add timeLeft as a dependency to re-rerun the effect
        // when we update it
      }
    }
  }, [timeLeft, run, status, slaTime]);

  useEffect(() => {
    secondsToHmsSLA(slaTime);
  }, [slaTime]);

  useEffect(() => {
    if (status === true) {
      // if (startTime > 0) {
      // if (!startTime) return;
      if (run === false) {
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

  function secondsToHmsSLA(d) {
    d = Number(d);
    if (d < 0) {
      setMinus("-");
      d = -d;
    }
    var h = Math.floor(d / 3600);
    var m = Math.floor((d % 3600) / 60);
    var s = Math.floor((d % 3600) % 60);

    var hDisplay = h > 0 ? h + (h === 1 ? "" : "") : h;
    var mDisplay = m > 0 ? m + (m === 1 ? "" : "") : m;
    var sDisplay = s > 0 ? s + (s === 1 ? "" : "") : s;
    setHourSLA(hDisplay);
    setMinuteSLA(mDisplay);
    setSecondSLA(sDisplay);
    return hDisplay + mDisplay + sDisplay;
  }

  function secondsToHms(d) {
    d = Number(d);
    var h = Math.floor(d / 3600);
    var m = Math.floor((d % 3600) / 60);
    var s = Math.floor((d % 3600) % 60);

    var hDisplay = h > 0 ? h + (h === 1 ? "" : "") : "0";
    var mDisplay = m > 0 ? m + (m === 1 ? "" : "") : "0";
    var sDisplay = s > 0 ? s + (s === 1 ? "" : "") : "0";
    setHour(hDisplay);
    setMinute(mDisplay);
    setSecond(sDisplay);
    return hDisplay + mDisplay + sDisplay;
  }

  useEffect(() => {
    secondsToHmsSLA(slaTime);
  }, [slaTime]);

  //
  const handleStop = () => {
    setRun(true);
    if (timeLeft < 0) {
      setResult1("Overdue");
    } else if (timeLeft > 0) {
      setResult1("Done");
    }
  };

  return (
    <>
      <table>
        <tbody>
          <tr>
            <td>SLA Name</td>
            <td>{item.name}</td>
          </tr>
          <tr>
            <td>SLA Time</td>
            <td>
              <input value={`${minus} ${hourSLA}:${miniteSLA}:${secondSLA}`} />
            </td>
          </tr>
          <tr>
            <td>Process Time</td>
            <td>
              <input value={`${hour}:${minite}:${second}`} />
            </td>
          </tr>
          <tr>
            <td></td>
            <td>
              <button
                onClick={() => {
                  handleStop();
                  let tmp = [...data];
                  tmp[index].status = true;
                  setData(tmp);
                }}
                disabled={status === false ? true : false}
              >
                Done
              </button>
            </td>
          </tr>
          <tr>
            <td>Result 1:</td>
            <td>{result1}</td>
          </tr>
          <tr>
            <td>Result 2:</td>
            <td>{result2}</td>
          </tr>
        </tbody>
      </table>
    </>
  );
};

export default SLA;
