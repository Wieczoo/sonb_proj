import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const Node = ({ id, status, onClick, isSelectedSource, isSelectedDestination }) => {
  let style = {
    border: '1px solid black',
    borderRadius: '50%', 
    width: '60px',
    height: '60px',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    margin: '10px',
    cursor: 'pointer',
    backgroundColor: 'lightgray',
    transition: 'background-color 0.3s ease, border 0.3s ease',
  };

  if (isSelectedSource) {
    style.backgroundColor = 'lightblue';
    style.border = '2px solid blue';
  } else if (isSelectedDestination) {
    style.backgroundColor = 'lightgreen';
    style.border = '2px solid green';
  }

  return (
    <div style={style} onClick={() => onClick(id)}>
      Węzeł {id}
      {}
    </div>
  );
};

function App() {
  const [serverIp, setServerIp] = useState('127.0.0.1');
  const [serverPort, setServerPort] = useState('8000');

  const [nodes, setNodes] = useState([]);
  const [selectedSource, setSelectedSource] = useState(null);
  const [selectedDestination, setSelectedDestination] = useState(null);
  const [errorType, setErrorType] = useState('none'); 
  const [dataBits,setDataBits] = useState(''); 
  const [errorCount, setErrorCount] = useState(1);
  const [dataKey, setDataKey] = useState('');
  const [logs, setLogs] = useState([]);

  const addLog = useCallback((message) => {
    setLogs(prevLogs => [`[${new Date().toLocaleTimeString()}] ${message}`, ...prevLogs]);
  }, []);

  const fetchNodes = async () => {
    try {
      const response = await axios.get(`http://${serverIp}:${serverPort}/simulation/nodes/`);
      const fetchedNodes = response.data.nodes || [];
      setNodes(
        fetchedNodes.map((node) => ({
          id: node.id,
          status: node.status || 'Idle',
        }))
      );
      addLog('Pobrano listę węzłów z serwera.');
    } catch (error) {
      addLog(`Błąd podczas pobierania węzłów: ${error.message}`);
    }
  };

  useEffect(() => {
    fetchNodes();
  }, [serverIp, serverPort]);

  const handleCreateTenNodes = async () => {
    try {
      const response = await axios.post(`http://${serverIp}:${serverPort}/simulation/nodes/ensure_ten_online/`);
      addLog(`Utworzono 10 węzłów: ${response.data.message || 'Sukces'}`);
      fetchNodes(); // Odśwież listę węzłów po utworzeniu
    } catch (error) {
      addLog(`Błąd podczas tworzenia węzłów: ${error.message}`);
    }
  };

  // Obsługa kliknięcia węzła
  const handleNodeClick = (nodeId) => {
    if (selectedSource === nodeId) {
      setSelectedSource(null);
      addLog(`Odznaczono węzeł źródłowy: ${nodeId}`);
    } else if (selectedDestination === nodeId) {
      setSelectedDestination(null);
      addLog(`Odznaczono węzeł docelowy: ${nodeId}`);
    } else if (!selectedSource) {
      setSelectedSource(nodeId);
      addLog(`Wybrano węzeł źródłowy: ${nodeId}`);
    } else if (!selectedDestination) {
      setSelectedDestination(nodeId);
      addLog(`Wybrano węzeł docelowy: ${nodeId}`);
    } else {
        addLog(`Najpierw odznacz obecne węzły, aby wybrać nowe.`);
    }
  };


  const handleStartSimulation = () => {
    if (!selectedSource || !selectedDestination) {
      addLog('BŁĄD: Proszę wybrać węzeł źródłowy i docelowy.');
      return;
    }
  
    addLog(`Rozpoczynanie symulacji: ${selectedSource} -> ${selectedDestination}. Typ błędu: ${errorType}`);
  
    axios.post(`http://${serverIp}:${serverPort}/simulation/simulate/`, {
      source_id: selectedSource,
      destination_id: selectedDestination,
      data: dataBits, 
      key: dataKey, 
      delay: 0.5, 
      packet_loss_percentage: 0.0, 
      error_params: { 
        error_count: errorCount
       ,error_type:  errorType}, 
    })
    .then(response => {
      debugger;
      addLog(`Symulacja zakończona sukcesem: ${JSON.stringify(response.data)}`);
    })
    .catch(error => {
      debugger;
      addLog(`Błąd podczas symulacji: ${error.message}`);
    });
  };



  return (
    <div style={{ fontFamily: 'Arial, sans-serif', padding: '20px' }}>
      <h1>Symulator Sieci Komputerowej z CRC</h1>
      <div style={{ marginBottom: '20px', padding: '10px', border: '1px solid #ccc' }}>
        <h2>Konfiguracja Serwera Symulacji</h2>
        <label>
          Adres IP Serwera:
          <input
            type="text"
            value={serverIp}
            onChange={(e) => setServerIp(e.target.value)}
            style={{ marginLeft: '10px', marginRight: '20px' }}
          />
        </label>
        <label>
          Port Serwera:
          <input
            type="text"
            value={serverPort}
            onChange={(e) => setServerPort(e.target.value)}
            style={{ marginLeft: '10px' }}
          />
        </label>
      
      </div>

      {/* Sekcja wizualizacji węzłów */}
      <h2>Wizualizacja Węzłów</h2>
      <p>Kliknij na węzeł, aby wybrać go jako źródło, a następnie na inny, aby wybrać cel.</p>
       <div style={{ display: 'flex', flexWrap: 'wrap', marginBottom: '20px', border: '1px dashed blue', padding: '10px' }}>
        {nodes.map((node) => (
          <Node
            key={node.id}
            id={node.id}
            status={node.status}
            onClick={handleNodeClick}
            isSelectedSource={node.id === selectedSource}
            isSelectedDestination={node.id === selectedDestination}
          />
        ))}
      </div>


      {/* Przycisk do tworzenia węzłów */}
      <div style={{ marginBottom: '20px', padding: '10px', border: '1px solid #ccc' }}>
        <button
          onClick={handleCreateTenNodes}
          style={{ padding: '10px 15px', cursor: 'pointer', backgroundColor: '#4CAF50', color: 'white', border: 'none', borderRadius: '5px' }}
        >
          Utwórz 10 węzłów
        </button>
      </div>

      {/* Sekcja kontroli symulacji */}
        <div style={{ marginBottom: '20px', padding: '10px', border: '1px solid #ccc' }}>
            <h2>Kontrola Symulacji</h2>
            <div>
           Wybrany węzeł źródłowy: <strong>{selectedSource || 'Brak'}</strong>
            </div>
             <div>
           Wybrany węzeł docelowy: <strong>{selectedDestination || 'Brak'}</strong>
            </div>
             <div style={{ marginTop: '10px' }}>
            <label htmlFor="errorType">Typ błędu do wprowadzenia:</label>
            <select
                id="errorType"
                value={errorType}
                onChange={(e) => setErrorType(e.target.value)}
                style={{ marginLeft: '10px', marginRight: '20px' }}
            >
                <option value="none">Brak błędu</option>
                <option value="single">Pojedyncze przekłamanie bitu</option> 
                <option value="double">Błędy podwójne</option>
                <option value="odd">Błędy o nieparzystej liczbie przekłamań</option> 
                <option value="burst">Błędy burstowe</option> 
            </select>
             </div>
             <div style={{ marginTop: '10px' }}>
            <label htmlFor="dataBits">Wprowadź bity do transmisji:</label>
            <input
                id="dataBits"
                type="text"
                value={dataBits}
                onChange={(e) => setDataBits(e.target.value)}
                style={{ marginLeft: '10px', width: '200px' }}
            />
             </div>
             <div style={{ marginTop: '10px' }}>
            <label htmlFor="dataBits">Wprowadź klucz do transmisji:</label>
            <input
                id="dataKey"
                type="text"
                value={dataKey}
                onChange={(e) => setDataKey(e.target.value)}
                style={{ marginLeft: '10px', width: '200px' }}
            />
             </div>
            <button
              onClick={handleStartSimulation}
              disabled={!selectedSource || !selectedDestination || !dataBits}
              style={{ marginTop: '15px', padding: '10px 15px', cursor: !selectedSource || !selectedDestination || !dataBits ? 'not-allowed' : 'pointer' }}
            >
              Rozpocznij Symulację Transmisji
            </button>
        </div>

         {/* Sekcja logów */}
        <div style={{ marginTop: '20px' }}>
            <h2>Logi Symulacji</h2>
            <textarea
                value={logs.join('\n')}
                readOnly
                style={{ width: '95%', height: '150px', marginTop: '10px', fontFamily: 'monospace', fontSize: '12px' }}
            />
        </div>

    </div>
  );
}

export default App;