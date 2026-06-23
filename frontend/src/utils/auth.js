export const saveAuthData = (
    token,
    role
) => {

    localStorage.setItem(
        "token",
        token
    );

    localStorage.setItem(
        "role",
        role
    );
};


export const logout = () => {

    localStorage.removeItem(
        "token"
    );

    localStorage.removeItem(
        "role"
    );
};


export const getRole = () => {

    return localStorage.getItem(
        "role"
    );
};

export const getToken = () => {

    return localStorage.getItem(
        "token"
    );
};


export const isAuthenticated =
    () => {

    return !!localStorage.getItem(
        "token"
    );
};
