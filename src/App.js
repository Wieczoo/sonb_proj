import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Stage, Layer, Circle, Line, Text } from 'react-konva';
import './App.css';

const NODE_RADIUS = 20;

const NetworkVisualizer = ({
  nodes,
  connections,
  onNodePositionChange,
  selectedSource,
  selectedDestination,
  onNodeClick,
  onBackgroundClick
}) => {
  return (
    <div className="network-visualizer-container">
      <Stage
        width={1000}
        height={300}
        onClick={(e) => {
          if (e.target === e.currentTarget) {
            onBackgroundClick();
          }
        }}
      >
        <Layer>
          {connections.map(connection => {
            const startNode = nodes.find(n => n.id === connection.source);
            const endNode = nodes.find(n => n.id === connection.target);
            if (!startNode || !endNode) return null;
            return (
              <Line
                key={`${connection.source}-${connection.target}`}
                points={[startNode.x, startNode.y, endNode.x, endNode.y]}
                stroke="gray"
                strokeWidth={2}
              />
            );
          })}
          {nodes.map(node => {
             console.log('Renderuję węzeł:', node.id);
            const isSelectedSource = node.id === selectedSource;
            const isSelectedDestination = node.id === selectedDestination;
            return (
              <Circle
              key={node.id}
              x={node.x}
              y={node.y}
              radius={NODE_RADIUS}
              fill={isSelectedSource ? 'lightblue' : isSelectedDestination ? 'lightgreen' : 'lightgray'}
              stroke="black"
              strokeWidth={1}
              draggable
              onDragMove={(e) => {
                const shape = e.target;
                const newX = Math.max(NODE_RADIUS, Math.min(800 - NODE_RADIUS, shape.x()));
                const newY = Math.max(NODE_RADIUS, Math.min(300 - NODE_RADIUS, shape.y()));
                shape.x(newX);
                shape.y(newY);
              }}
              onDragEnd={(e) => {
                onNodePositionChange(node.id, e.target.x(), e.target.y());
              }}
              onClick={(e) => {
                e.cancelBubble = true;
                onNodeClick(node.id);
              }}
            />
            
            );
          })}
          {nodes.map(node => (
            <Text
              key={`label-${node.id}`}
              x={node.x - NODE_RADIUS / 2}
              y={node.y + NODE_RADIUS + 10}
              text={`Węzeł ${node.id}`}
              fontSize={12}
              align="center"
            />
          ))}
        </Layer>
      </Stage>
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
  const [dataBits, setDataBits] = useState('');
  const [errorCount, setErrorCount] = useState(1);
  const [dataKey, setDataKey] = useState('');
  const [logs, setLogs] = useState([]);
  const [connections, setConnections] = useState([]);

  const addLog = useCallback((message) => {
    setLogs(prevLogs => [`[${new Date().toLocaleTimeString()}] ${message}`, ...prevLogs]);
  }, []);

  const fetchNodes = async () => {
    try {
      const response = await axios.get(`http://${serverIp}:${serverPort}/simulation/nodes/`);
      const fetchedNodes = response.data.nodes || [];
      const initialNodesWithPositions = fetchedNodes.map(node => ({
        id: node.id,
        status: node.status || 'Idle',
        x: Math.random() * (800 - 2 * NODE_RADIUS) + NODE_RADIUS,
        y: Math.random() * (300 - 2 * NODE_RADIUS) + NODE_RADIUS,
      }));
      
      
  
      setNodes(initialNodesWithPositions);
  
      // Sprawdź, czy wybrane węzły jeszcze istnieją
      const fetchedIds = fetchedNodes.map(n => n.id);
      if (!fetchedIds.includes(selectedSource)) {
        setSelectedSource(null);
        addLog('Wybrany węzeł źródłowy został usunięty.');
      }
      if (!fetchedIds.includes(selectedDestination)) {
        setSelectedDestination(null);
        addLog('Wybrany węzeł docelowy został usunięty.');
      }
  
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
      fetchNodes();
    } catch (error) {
      addLog(`Błąd podczas tworzenia węzłów: ${error.message}`);
    }
  };

  const handleShutdownMaster = async () => {
    if (!selectedSource) {
      addLog('Nie wybrano węzła źródłowego do wyłączenia.');
      return;
    }

    try {
      await axios.post(`http://${serverIp}:${serverPort}/simulation/shutdown_master/`, {
        source_id: selectedSource,
      });
      addLog(`Węzeł źródłowy ${selectedSource} został wyłączony.`);
      fetchNodes();
    } catch (error) {
      addLog(`Błąd przy wyłączaniu węzła źródłowego ${selectedSource}: ${error.message}`);
    }
  };

  const handleShutdownNode = async () => {
    if (!selectedDestination) {
      addLog('Nie wybrano węzła docelowego do wyłączenia.');
      return;
    }

    try {
      await axios.post(`http://${serverIp}:${serverPort}/simulation/shutdown_node/`, {
        destination_id: selectedDestination,
      });
      addLog(`Węzeł docelowy ${selectedDestination} został wyłączony.`);
      fetchNodes();
    } catch (error) {
      addLog(`Błąd przy wyłączaniu węzła docelowego ${selectedDestination}: ${error.message}`);
    }
  };

  const handleNodeClick = (nodeId) => {
    if (selectedSource === null) {
      setSelectedSource(nodeId);
      setSelectedDestination(null);
      addLog(`Wybrano węzeł źródłowy: ${nodeId}`);
    } else if (selectedDestination === null) {
      if (selectedSource !== nodeId) {
        setSelectedDestination(nodeId);
        setConnections(prev => [...prev, { source: selectedSource, target: nodeId }]);
        addLog(`Wybrano węzeł docelowy: ${nodeId} i utworzono połączenie.`);
      } else {
        setSelectedSource(null);
        setSelectedDestination(null);
        addLog(`Odznaczono węzeł źródłowy: ${nodeId}`);
      }
    } else {
      setSelectedSource(nodeId);
      setSelectedDestination(null);
      setConnections([]);
      addLog(`Wybrano nowy węzeł źródłowy: ${nodeId}, zresetowano cel i połączenia.`);
    }
  };

  const handleNodePositionChange = (nodeId, newX, newY) => {
    setNodes(prevNodes =>
      prevNodes.map(node =>
        node.id === nodeId ? { ...node, x: newX, y: newY } : node
      )
    );
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
        error_count: errorCount,
        error_type: errorType,
      },
    })
      .then(response => {
        addLog(`Symulacja zakończona sukcesem: ${JSON.stringify(response.data)}`);
      })
      .catch(error => {
        addLog(`Błąd podczas symulacji: ${error.message}`);
      });
  };

  return (
    <div className="container">
      <h1 className="heading">Symulator Sieci Komputerowej z CRC</h1>

      {/* Server Configuration */}
      <div className="server-config">
        <h2 className="sub-heading">Konfiguracja Serwera Symulacji</h2>
        <div className="input-row-centered">
          <div className="input-block">
            <label className="label">Adres IP Serwera:</label>
            <input
              type="text"
              value={serverIp}
              onChange={(e) => setServerIp(e.target.value)}
              className="input"
            />
          </div>
          <div className="input-block">
            <label className="label">Port Serwera:</label>
            <input
              type="text"
              value={serverPort}
              onChange={(e) => setServerPort(e.target.value)}
              className="input"
            />
          </div>
        </div>
      </div>

      {/* Network Visualization */}
      <div className="visualization-section">
        <h2 className="sub-heading">Wizualizacja Sieci</h2>
        <p className="instruction">Kliknij węzeł, aby wybrać źródło i cel. Kliknij tło, aby odznaczyć wszystko.</p>
        <NetworkVisualizer
          nodes={nodes}
          connections={connections}
          onNodePositionChange={handleNodePositionChange}
          selectedSource={selectedSource}
          selectedDestination={selectedDestination}
          onNodeClick={handleNodeClick}
          onBackgroundClick={() => {
            setSelectedSource(null);
            setSelectedDestination(null);
            setConnections([]);
            addLog('Odznaczono wszystkie węzły.');
          }}
        />
      </div>

      {/* Actions */}
      <div className="actions">
        <button onClick={handleCreateTenNodes} className="button">Utwórz 10 węzłów</button>
        <button onClick={handleShutdownMaster} className="button button-danger" disabled={!selectedSource}>
          Wyłącz źródłowy węzeł
        </button>
        <button onClick={handleShutdownNode} className="button button-warning" disabled={!selectedDestination}>
          Wyłącz docelowy węzeł
        </button>
      </div>

      {/* Simulation Control */}
      <div className="simulation-control">
        <h2 className="sub-heading">Kontrola Symulacji</h2>
        <div className="info">
          Wybrany węzeł źródłowy: <strong>{selectedSource || 'Brak'}</strong>
        </div>
        <div className="info">
          Wybrany węzeł docelowy: <strong>{selectedDestination || 'Brak'}</strong>
        </div>
        {/* Error options */}
        <div className="form-group">
          <label className="label">Typ błędu:</label>
          <select
            className="select"
            value={errorType}
            onChange={(e) => setErrorType(e.target.value)}
          >
            <option value="none">Brak</option>
            <option value="single">Pojedynczy</option>
            <option value="double">Podwójny</option>
            <option value="odd">Nieparzysty</option>
            <option value="burst">Burstowy</option>
          </select>
        </div>
        {/* Data bits */}
        <div className="form-group">
          <label className="label">Dane:</label>
          <input
            className="input"
            value={dataBits}
            onChange={(e) => setDataBits(e.target.value)}
          />
        </div>
        {/* Data key */}
        <div className="form-group">
          <label className="label">Klucz CRC:</label>
          <input
            className="input"
            value={dataKey}
            onChange={(e) => setDataKey(e.target.value)}
          />
        </div>

        <button
          className={`button button-primary ${(!selectedSource || !selectedDestination || !dataBits) ? 'button-disabled' : ''}`}
          onClick={handleStartSimulation}
          disabled={!selectedSource || !selectedDestination || !dataBits}
        >
          Rozpocznij Symulację
        </button>
      </div>

      {/* Logs */}
      <div className="logs">
        <h2 className="sub-heading">Logi</h2>
        <textarea value={logs.join('\n')} readOnly className="log-textarea" />
      </div>
    </div>
  );
}

export default App;
