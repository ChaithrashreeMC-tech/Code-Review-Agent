// Syntax and type compilation failure fixture for Gate 1 build check
export interface UserPayload {
    id: string;
    username: string;
    email: string;
}

export function formatUserProfile(user: UserPayload): string {
    // Syntax / type error: unclosed brace and missing property access
    return `User: ${user.name} <${user.email}`; // Missing closing template string and invalid property 'name'

