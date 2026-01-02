import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { 
  MessageSquare, 
  BarChart3, 
  History, 
  Settings, 
  LogOut,
  Zap,
  Shield,
  Menu,
  X
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";

interface NavItemProps {
  to: string;
  icon: React.ReactNode;
  label: string;
  isActive: boolean;
  onClick?: () => void;
}

const NavItem = ({ to, icon, label, isActive, onClick }: NavItemProps) => (
  <Link
    to={to}
    onClick={onClick}
    className={cn(
      "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200",
      isActive
        ? "bg-primary/10 text-primary border border-primary/20"
        : "text-muted-foreground hover:text-foreground hover:bg-accent"
    )}
  >
    {icon}
    <span>{label}</span>
  </Link>
);

interface SidebarContentProps {
  isAdmin?: boolean;
  onNavClick?: () => void;
}

const SidebarContent = ({ isAdmin = false, onNavClick }: SidebarContentProps) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { userInfo, signOut } = useAuth();
  const currentPath = location.pathname;

  const handleLogout = async () => {
    try {
      await signOut();
      toast.success('Logged out successfully');
      navigate('/login');
    } catch (error) {
      toast.error('Failed to logout');
    }
  };

  const navItems = [
    { to: "/", icon: <MessageSquare className="w-4 h-4" />, label: "Query" },
    { to: "/usage", icon: <BarChart3 className="w-4 h-4" />, label: "Usage" },
    { to: "/history", icon: <History className="w-4 h-4" />, label: "History" },
  ];

  const adminItems = [
    { to: "/admin", icon: <Shield className="w-4 h-4" />, label: "Admin Panel" },
    { to: "/admin/metrics", icon: <BarChart3 className="w-4 h-4" />, label: "Usage Metrics" },
  ];

  return (
    <div className="flex flex-col h-full">
      {/* Logo */}
      <div className="p-6 border-b border-sidebar-border">
        <Link to="/" className="flex items-center gap-3" onClick={onNavClick}>
          <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center glow-effect">
            <Zap className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h1 className="font-semibold text-foreground">IntelRouter</h1>
            <p className="text-xs text-muted-foreground">Intelligent API Gateway</p>
          </div>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-3 px-3">
          Main
        </p>
        {navItems.map((item) => (
          <NavItem
            key={item.to}
            to={item.to}
            icon={item.icon}
            label={item.label}
            isActive={currentPath === item.to}
            onClick={onNavClick}
          />
        ))}

        {isAdmin && (
          <>
            <div className="pt-4 mt-4 border-t border-sidebar-border">
              <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-3 px-3">
                Admin
              </p>
              {adminItems.map((item) => (
                <NavItem
                  key={item.to}
                  to={item.to}
                  icon={item.icon}
                  label={item.label}
                  isActive={currentPath === item.to}
                  onClick={onNavClick}
                />
              ))}
            </div>
          </>
        )}
      </nav>

      {/* User Section */}
      <div className="p-4 border-t border-sidebar-border">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-9 h-9 rounded-lg bg-accent flex items-center justify-center">
            <span className="text-sm font-medium text-foreground">
              {userInfo?.email?.[0]?.toUpperCase() || 'U'}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-foreground truncate">
              {userInfo?.email || 'User'}
            </p>
            <p className="text-xs text-muted-foreground capitalize">
              {userInfo?.role || 'user'}
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <button 
            onClick={onNavClick}
            className="flex-1 flex items-center justify-center gap-2 px-3 py-2 text-xs text-muted-foreground hover:text-foreground hover:bg-accent rounded-lg transition-colors"
          >
            <Settings className="w-3.5 h-3.5" />
            Settings
          </button>
          <button 
            onClick={handleLogout}
            className="flex-1 flex items-center justify-center gap-2 px-3 py-2 text-xs text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded-lg transition-colors"
          >
            <LogOut className="w-3.5 h-3.5" />
            Logout
          </button>
        </div>
      </div>
    </div>
  );
};

interface SidebarProps {
  isAdmin?: boolean;
}

export const Sidebar = ({ isAdmin = false }: SidebarProps) => {
  const { userInfo } = useAuth();
  const actualIsAdmin = userInfo?.role === 'admin';
  
  return (
    <aside className="hidden lg:flex w-64 h-screen bg-sidebar border-r border-sidebar-border flex-col">
      <SidebarContent isAdmin={actualIsAdmin} />
    </aside>
  );
};

export const MobileNav = ({ isAdmin = false }: SidebarProps) => {
  const [open, setOpen] = useState(false);
  const { userInfo } = useAuth();
  const actualIsAdmin = userInfo?.role === 'admin';

  return (
    <div className="lg:hidden fixed top-0 left-0 right-0 z-50 bg-sidebar/95 backdrop-blur-lg border-b border-sidebar-border">
      <div className="flex items-center justify-between px-4 h-16">
        <Link to="/" className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-primary/10 flex items-center justify-center">
            <Zap className="w-4 h-4 text-primary" />
          </div>
          <span className="font-semibold text-foreground">IntelRouter</span>
        </Link>

        <Sheet open={open} onOpenChange={setOpen}>
          <SheetTrigger asChild>
            <Button variant="ghost" size="icon" className="text-foreground">
              <Menu className="w-5 h-5" />
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="w-72 p-0 bg-sidebar border-sidebar-border">
            <SidebarContent isAdmin={actualIsAdmin} onNavClick={() => setOpen(false)} />
          </SheetContent>
        </Sheet>
      </div>
    </div>
  );
};
