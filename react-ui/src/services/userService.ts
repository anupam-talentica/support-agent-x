export interface User {
  phone: string;
  role: 'admin' | 'customer';
  isAuthenticated: boolean;
}

export class UserService {
  // Define admin phone numbers (in real app, this would come from backend)
  private static readonly ADMIN_PHONES = ['9999999999', '8888888888', '7777777777'];
  
  /**
   * Check if a phone number belongs to an admin user
   */
  static isAdmin(phoneNumber: string): boolean {
    return this.ADMIN_PHONES.includes(phoneNumber);
  }
  
  /**
   * Get current authenticated user from localStorage
   */
  static getCurrentUser(): User | null {
    const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true';
    const phone = localStorage.getItem('userPhone');
    
    if (!isAuthenticated || !phone) {
      return null;
    }
    
    return {
      phone,
      role: this.isAdmin(phone) ? 'admin' : 'customer',
      isAuthenticated: true
    };
  }
  
  /**
   * Get user role for a specific phone number
   */
  static getUserRole(phoneNumber: string): 'admin' | 'customer' {
    return this.isAdmin(phoneNumber) ? 'admin' : 'customer';
  }
  
  /**
   * Check if current user is admin
   */
  static isCurrentUserAdmin(): boolean {
    const user = this.getCurrentUser();
    return user?.role === 'admin' || false;
  }
  
  /**
   * Get display name for role
   */
  static getRoleDisplayName(role: 'admin' | 'customer'): string {
    return role === 'admin' ? 'Administrator' : 'Customer';
  }
}

export const userService = UserService;