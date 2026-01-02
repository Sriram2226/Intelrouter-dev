import { ReactNode } from "react";
import { Sidebar, MobileNav } from "./Sidebar";
import { useAuth } from "@/contexts/AuthContext";

interface DashboardLayoutProps {
  children: ReactNode;
}

export const DashboardLayout = ({ children }: DashboardLayoutProps) => {
  const { userInfo } = useAuth();
  const isAdmin = userInfo?.role === 'admin';

  return (
    <div className="flex min-h-screen w-full bg-background">
      {/* Desktop Sidebar */}
      <Sidebar isAdmin={isAdmin} />
      
      {/* Mobile Navigation */}
      <MobileNav isAdmin={isAdmin} />
      
      {/* Main Content */}
      <main className="flex-1 lg:ml-64 overflow-auto">
        <div className="p-4 pt-20 lg:pt-8 lg:p-8">
          {children}
        </div>
      </main>
    </div>
  );
};
