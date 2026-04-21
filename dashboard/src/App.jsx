import React, { useState, useEffect } from 'react';
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
  Settings
} from 'lucide-react';
import manifest from './data/manifest.json';

const App = () => {
  const [selectedItem, setSelectedItem] = useState(null);
  const [markdownContent, setMarkdownContent] = useState('');
  const [loading, setLoading] = useState(false);

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

  const renderContent = () => {
    if (!selectedItem) {
      return (
        <div className="empty-state">
          <LayoutDashboard size={64} color="#CFB87C" style={{ opacity: 0.5, marginBottom: 24 }} />
          <h2>Omission Project Dashboard</h2>
          <p>Select a figure or progress report from the sidebar to begin.</p>
        </div>
      );
    }

    if (selectedItem.type === 'report') {
      return (
        <div className="viewer-container">
          <div className="figure-card">
            <div className="figure-card-header">
              <h3>Progress Report: {selectedItem.title}</h3>
              <FileText size={20} color="#CFB87C" />
            </div>
            <div className="markdown-container">
              <ReactMarkdown>{markdownContent}</ReactMarkdown>
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="viewer-container">
        {selectedItem.files.map((file, idx) => (
          <div className="figure-card" key={idx}>
            <div className="figure-card-header">
              <h3>{file}</h3>
              <Activity size={20} color="#CFB87C" />
            </div>
            <div className="figure-iframe-container">
              <iframe 
                src={`${selectedItem.baseUrl}/${file}`} 
                className="figure-iframe"
                title={file}
              />
            </div>
          </div>
        ))}
        
        {selectedItem.has_readme && (
          <div className="figure-card">
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

  return (
    <>
      <div className="sidebar">
        <div className="sidebar-header">
          <h1>Omission</h1>
        </div>
        
        <div className="sidebar-section">
          <div className="sidebar-section-title">Figures (Phase 1-5)</div>
          {manifest.figures.map(fig => (
            <div 
              key={fig.id} 
              className={`nav-item ${selectedItem?.id === fig.id ? 'active' : ''}`}
              onClick={() => setSelectedItem({ ...fig, type: 'figure' })}
            >
              <Zap size={16} />
              <span>{fig.title}</span>
              <ChevronRight size={14} style={{ marginLeft: 'auto', opacity: 0.5 }} />
            </div>
          ))}
        </div>

        <div className="sidebar-section">
          <div className="sidebar-section-title">Progress Reports</div>
          {manifest.reports.map(report => (
            <div 
              key={report.id} 
              className={`nav-item ${selectedItem?.id === report.id ? 'active' : ''}`}
              onClick={() => setSelectedItem({ ...report, type: 'report' })}
            >
              <FileText size={16} />
              <span>{report.title}</span>
              <ChevronRight size={14} style={{ marginLeft: 'auto', opacity: 0.5 }} />
            </div>
          ))}
        </div>
      </div>

      <div className="main-content">
        <div className="header">
          <div className="header-title">
            {selectedItem ? (
              <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                {selectedItem.type === 'figure' ? <Activity size={18} color="#CFB87C" /> : <FileText size={18} color="#CFB87C" />}
                {selectedItem.title}
              </span>
            ) : 'Overview'}
          </div>
          <div style={{ display: 'flex', gap: 16 }}>
            <Settings size={20} color="#666" style={{ cursor: 'pointer' }} />
          </div>
        </div>
        
        {renderContent()}
      </div>
    </>
  );
};

export default App;
