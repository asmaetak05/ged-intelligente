import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import useUIStore from '../store/useUIStore';

const useKeyboardShortcuts = () => {
  const navigate = useNavigate();
  const toggleDarkMode = useUIStore((state) => state.toggleDarkMode);

  useEffect(() => {
    const handleKeyDown = (e) => {
      // Cmd/Ctrl + K => Focus search / Go to search
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        navigate('/search');
      }

      // Cmd/Ctrl + J => Toggle dark mode
      if ((e.metaKey || e.ctrlKey) && e.key === 'j') {
        e.preventDefault();
        toggleDarkMode();
      }

      // Esc => might want to close modals here
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [navigate, toggleDarkMode]);
};

export default useKeyboardShortcuts;
