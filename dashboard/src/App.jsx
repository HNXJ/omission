import React, { useState, useEffect } from 'react';
import { Routes, Route, Link, NavLink, useLocation, useParams, Navigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { 
  BarChart3, 
  FileText, 
  LayoutDashboard, 
  ChevronRight, 
  ExternalLink,
  Activity,
  Layers,
  Zap,
  Eye,
  Settings,
  Maximize2,
  X,
  ShieldCheck,
  TrendingUp,
  Clock,
  Terminal as TerminalIcon,
  ChevronDown
} from 'lucide-react';
import manifest from './data/manifest.json';
import scoreboard from './data/scoreboard.json';

const PHASES = [
  { id: 'p1', title: 'Phase 1: Baseline & PSTH', range: [1, 4], path: '/phase/1' },
  { id: 'p2', title: 'Phase 2: Spectral & Coordination', range: [5, 11], path: '/phase/2' },
  { id: 'p3', title: 'Phase 3: Connectivity & Granger', range: [12, 20], path: '/phase/3' },
  { id: 'p4', title: 'Phase 4: Decoding & Behavior', range: [21, 30], path: '/phase/4' },
  { id: 'p5', title: 'Phase 5: State-Space & RNN', range: [31, 50], path: '/phase/5' }
];

const TerminalTicker = () => (
  <div className="terminal-ticker">
    <div className="ticker-item">
      <ShieldCheck size={14} color="#000" />
      <span className="ticker-label">STATUS:</span>
      <span className="ticker-value">{scoreboard.system_status}</span>
    </div>
    <div className="ticker-item">
      <Activity size={14} color="#000" />
      <span className="ticker-label">PHASE:</span>
      <span className="ticker-value">{scoreboard.active_phase}</span>
    </div>
    <div className="ticker-divider"></div>
    <div className="ticker-item">
      <TrendingUp size={14} color="#000" />
      <span className="ticker-label">SESSIONS:</span>
      <span className="ticker-value">{scoreboard.metrics.sessions}</span>
    </div>
    <div className="ticker-item">
      <Zap size={14} color="#000" />
      <span className="ticker-label">LATENCY:</span>
      <span className="ticker-value">{scoreboard.metrics.latency_onset}</span>
    </div>
    <div className="ticker-item">
      <Layers size={14} color="#000" />
      <span className="ticker-label">UNITS:</span>
      <span className="ticker-value">{scoreboard.metrics.units}</span>
    </div>
  </div>
);

const TopNav = () => (
  <nav className="top-nav">
    <div className="top-nav-logo">OMISSION</div>
    <div className="top-nav-links">
      <NavLink to="/scoreboard" className={({ isActive }) => `top-nav-link ${isActive ? 'active' : ''}`}>
        Scoreboard
      </NavLink>
      {PHASES.map(phase => (
        <NavLink 
          key={phase.id} 
          to={phase.path} 
          className={({ isActive }) => `top-nav-link ${isActive ? 'active' : ''}`}
        >
          {phase.id.toUpperCase()}
        </NavLink>
      ))}
      <NavLink to="/reports" className={({ isActive }) => `top-nav-link ${isActive ? 'active' : ''}`}>
        Reports
      </NavLink>
    </div>
  </nav>
);

const App = () => {
  const [selectedItem, setSelectedItem] = useState(null);
  const [markdownContent, setMarkdownContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [modalFile, setModalFile] = useState(null);
  const [viewMode, setViewMode] = useState('gallery');
  const [expandedPhases, setExpandedPhases] = useState(['p1', 'p2', 'p3', 'p4', 'p5']);

  useEffect(() => {
    if (selectedItem) {
      if (selectedItem.type === 'report' || selectedItem.has_readme) {
        setLoading(true);
        const url = selectedItem.type === 'report' 
          ? selectedItem.url 
          : `${selectedItem.baseUrl}/README.md`;
        
        fetch(url)
          .then(res => res.text())
          .then(text => {
            setMarkdownContent(text);
            setLoading(false);
          })
          .catch(err => {
            console.error('Failed to fetch markdown:', err);
            setMarkdownContent('Error loading content.');
            setLoading(false);
          });
      }
    }
  }, [selectedItem]);

  const togglePhase = (phaseId) => {
    setExpandedPhases(prev => 
      prev.includes(phaseId) ? prev.filter(id => id !== phaseId) : [...prev, phaseId]
    );
  };

  const openModal = (file) => {
    setModalFile(`${selectedItem.baseUrl}/${file}`);
  };

  const closeModal = () => {
    setModalFile(null);
  };

  const getStatusColor = (status) => {
    switch(status) {
      case 'awesome': return '#CFB87C';
      case 'pass': return '#4CAF50';
      case 'running': return '#2196F3';
      case 'queued': return '#9E9E9E';
      case 'fail': return '#F44336';
      case 'pending agent action': return '#9400D3';
      case 'pending user action': return '#FF9800';
      default: return '#333';
    }
  };

  const [viewFilter, setViewFilter] = useState('both'); // 'both', 'aaab', 'axab'

  const getFiguresForPhase = (phase) => {
    return manifest.figures.filter(fig => fig.phase === parseInt(phase.id.replace('p', '')));
  };

  const filterFiles = (files) => {
    if (viewFilter === 'both') return files;
    // Omission PSTHs (f002) are usually specific files, but for traces (f003+) they have conditions
    if (viewFilter === 'aaab') return files.filter(f => 
      f.toLowerCase().includes('aaab') || 
      f.toLowerCase().includes('standard') ||
      (selectedItem.id === 'f002' && !f.toLowerCase().includes('csd') && !f.toLowerCase().includes('timeline')) // f002 defaults to showing both; this needs manifest metadata
    );
    if (viewFilter === 'axab') return files.filter(f => 
      f.toLowerCase().includes('axab') || 
      f.toLowerCase().includes('omission')
    );
    return files;
  };

  const renderScoreboard = () => (
    <div className="scoreboard-container">
      <div className="scoreboard-header">
        <BarChart3 size={24} color="#CFB87C" />
        <h2>Analytical Scoreboard Ledger</h2>
      </div>
      <table className="scoreboard-table">
        <thead>
          <tr>
            <th>Module</th>
            <th>Last Run</th>
            <th>Status</th>
            <th>Audit Score</th>
            <th>Notes & Remediation</th>
          </tr>
        </thead>
        <tbody>
          {scoreboard.ledger.map((entry, idx) => (
            <tr key={idx}>
              <td>
                <div className="bold">{entry.analysis}</div>
                <div className="dim">{entry.file}</div>
              </td>
              <td className="dim"><Clock size={12} /> {entry.date} {entry.time}</td>
              <td>
                <span className="status-badge" style={{ backgroundColor: getStatusColor(entry.status) }}>
                  {entry.status}
                </span>
              </td>
              <td className="score-cell" style={{ color: entry.score >= 75 ? '#4CAF50' : '#F44336' }}>
                {entry.score}/100
              </td>
              <td className="notes-cell">
                <div className="notes-text">{entry.notes}</div>
                <div className="code-ref"><TerminalIcon size={10} /> {entry.code}</div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  const renderStats = (stats) => {
    if (!stats || Object.keys(stats).length === 0) return null;
    
    // Select the correct stats slice based on viewFilter
    let activeStats = stats;
    if (stats.both) {
      activeStats = stats[viewFilter] || stats.both;
    }
    
    if (Object.keys(activeStats).length === 0) return (
      <div className="figure-card full-width">
        <div className="figure-card-header">
          <h3>Population Statistics (Standard Filter active - No Coding Data)</h3>
        </div>
      </div>
    );

    return (
      <div className="figure-card full-width">
        <div className="figure-card-header">
          <h3>Population Statistics (11 Areas) - {viewFilter.toUpperCase()} View</h3>
          <ShieldCheck size={20} color="#CFB87C" />
        </div>
        <div className="stats-grid">
          {Object.entries(activeStats).map(([area, s]) => (
            <div key={area} className="stat-unit">
              <div className="stat-unit-area">{area}</div>
              <div className="stat-unit-tier" style={{ color: getStatusColor(s.tier ? s.tier.toLowerCase() : 'awesome') }}>
                {s.tier || s.label || 'Sig-k'} {s.stars || ''}
              </div>
              <div className="stat-unit-meta">
                {s.n !== undefined ? `count=${s.n}` : (s.p !== undefined ? `p=${s.p.toExponential(2)} | n=${s.n_units || s.n_stable || '?'}` : `count=${s.n_s_plus || 0}/${s.n_o_plus || 0}`)}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderContent = () => {
    const location = useLocation();
    const isScoreboard = location.pathname === '/scoreboard';
    
    if (isScoreboard) return renderScoreboard();
    
    if (!selectedItem) {
      return (
        <div className="empty-state">
          <LayoutDashboard size={64} color="#CFB87C" style={{ opacity: 0.5, marginBottom: 24 }} />
          <h2>Omission Terminal</h2>
          <p>Select a module from the hierarchy to begin interrogation.</p>
        </div>
      );
    }

    return (
      <div className="viewer-container">
        {renderStats(selectedItem.stats)}
        
        <div className="gallery-grid">
          {filterFiles(selectedItem.files).map((file, idx) => (
            <div className="figure-card" key={idx}>
              <div className="figure-card-header">
                <h3>{file}</h3>
                <div className="card-actions">
                  <Maximize2 size={18} color="#CFB87C" onClick={() => openModal(file)} style={{ cursor: 'pointer' }} />
                  <Activity size={18} color="#666" />
                </div>
              </div>
              <div className="figure-iframe-container mini">
                <iframe src={`${selectedItem.baseUrl}/${file}`} className="figure-iframe" title={file} />
              </div>
            </div>
          ))}
        </div>
        {selectedItem.has_readme && (
          <div className="figure-card full-width">
            <div className="figure-card-header">
              <h3>Methodology & Interpretation</h3>
              <Layers size={20} color="#CFB87C" />
            </div>
            <div className="markdown-container">
              {loading ? <p>Loading methodology...</p> : <ReactMarkdown>{markdownContent}</ReactMarkdown>}
            </div>
          </div>
        )}
      </div>
    );
  };

  const Sidebar = () => {
    const location = useLocation();
    
    // Determine if we are in a phase route
    const phaseMatch = location.pathname.match(/\/phase\/(\d+)/);
    const activePhaseId = phaseMatch ? `p${phaseMatch[1]}` : null;
    const isScoreboard = location.pathname === '/scoreboard';
    const isReports = location.pathname === '/reports';

    return (
      <div className="sidebar">
        <div className="sidebar-header">
          <h1>Analysis</h1>
        </div>

        {isScoreboard && (
          <div className="sidebar-section">
            <div className="sidebar-section-title">Scoreboard Navigation</div>
            <div className="nav-item active">
              <BarChart3 size={16} />
              <span>Current Ledger</span>
            </div>
          </div>
        )}

        {activePhaseId && (
          <div className="sidebar-section">
            <div className="sidebar-section-title">
              {PHASES.find(p => p.id === activePhaseId)?.title || 'Phase Modules'}
            </div>
            {getFiguresForPhase(PHASES.find(p => p.id === activePhaseId)).map(fig => (
              <div 
                key={fig.id} 
                className={`nav-item ${selectedItem?.id === fig.id ? 'active' : ''}`}
                onClick={() => setSelectedItem({ ...fig, type: 'figure' })}
              >
                <Zap size={14} />
                <span>{fig.title}</span>
              </div>
            ))}
          </div>
        )}

        {isReports && (
          <div className="sidebar-section">
            <div className="sidebar-section-title">Protocol Reports</div>
            {manifest.reports.map(report => (
              <div 
                key={report.id} 
                className={`nav-item ${selectedItem?.id === report.id ? 'active' : ''}`}
                onClick={() => setSelectedItem({ ...report, type: 'report' })}
              >
                <FileText size={16} />
                <span>{report.title}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <>
      <TerminalTicker />
      <TopNav />
      <div className="layout-wrapper">
        <Sidebar />
        <div className="main-content">
          <div className="header">
            <div className="header-title">
              {selectedItem ? selectedItem.title : 'Analytical Terminal'}
            </div>
            
            <div className="header-actions">
              <div className="filter-toggle">
                <button 
                  className={`filter-btn ${viewFilter === 'both' ? 'active' : ''}`}
                  onClick={() => setViewFilter('both')}
                >BOTH</button>
                <button 
                  className={`filter-btn ${viewFilter === 'aaab' ? 'active' : ''}`}
                  onClick={() => setViewFilter('aaab')}
                >STANDARD</button>
                <button 
                  className={`filter-btn ${viewFilter === 'axab' ? 'active' : ''}`}
                  onClick={() => setViewFilter('axab')}
                >OMISSION</button>
              </div>
              <Settings size={20} color="#666" style={{ cursor: 'pointer' }} />
            </div>
          </div>
          <div className="scroll-wrapper">
            <Routes>
              <Route path="/" element={<Navigate to={`/phase/${scoreboard.active_phase.replace('Phase ', '')}`} replace />} />
              <Route path="/scoreboard" element={renderScoreboard()} />
              <Route path="/phase/:id" element={renderContent()} />
              <Route path="/reports" element={renderContent()} />
            </Routes>
          </div>
        </div>
      </div>

      {modalFile && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>High-Fidelity Terminal View</h3>
              <X size={24} color="#FFF" style={{ cursor: 'pointer' }} onClick={closeModal} />
            </div>
            <iframe src={modalFile} className="modal-iframe" title="Maximized View" />
          </div>
        </div>
      )}
    </>
  );
};

export default App;


