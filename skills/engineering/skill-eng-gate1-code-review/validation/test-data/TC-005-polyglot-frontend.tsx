import React from 'react';

interface ProductViewProps {
    id: string;
    title: string;
    price: number;
}

export const ProductView: React.FC<ProductViewProps> = ({ id, title, price }) => {
    return (
        <div className="product-card" data-testid={`product-${id}`}>
            <h3>{title}</h3>
            <p>${price.toFixed(2)}</p>
        </div>
    );
};

