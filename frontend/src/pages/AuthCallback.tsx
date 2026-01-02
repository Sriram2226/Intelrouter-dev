import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { supabase } from '@/lib/supabase';
import { Loader2 } from 'lucide-react';

const AuthCallback = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // Get the session from the URL hash/fragment
        const { data: { session }, error } = await supabase.auth.getSession();
        
        if (error) {
          console.error('Error getting session:', error);
          navigate('/login?error=authentication_failed');
          return;
        }

        if (session) {
          // Session is automatically handled by AuthContext via onAuthStateChange
          // Just redirect to home
          navigate('/');
        } else {
          navigate('/login?error=no_session');
        }
      } catch (err) {
        console.error('Callback error:', err);
        navigate('/login?error=callback_failed');
      }
    };

    handleCallback();
  }, [navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center space-y-4">
        <Loader2 className="h-8 w-8 animate-spin mx-auto" />
        <p className="text-muted-foreground">Completing sign in...</p>
      </div>
    </div>
  );
};

export default AuthCallback;

