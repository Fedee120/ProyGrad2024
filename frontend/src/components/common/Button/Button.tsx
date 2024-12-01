import './buttonStyles.scss'
const Button = ({ 
        children = "Continue", 
        onClick, 
        className, 
        disabled = false, 
        loading = false, 
        icon, 
        iconPosition="left", 
        type='button',
        variant='primary',
        fullWidth = false,
        size = 'medium'
    }: { 
        children?: React.ReactNode, 
        onClick?: () => void, 
        className?: string, 
        disabled?: boolean, 
        loading?: boolean, 
        icon?: React.ReactNode, 
        iconPosition?: 'left' | 'right', 
        type?: 'button' | 'submit' | 'reset',
        variant?: 'primary' | 'secondary' | 'danger',
        fullWidth?: boolean,
        size?: 'small' | 'medium' | 'large'
    }) => {
    return (
        <button className={`button-container ${variant} ${className} ${disabled && 'disabled'} ${fullWidth && 'full-width'} ${size && `size-${size}`}`} type={type} disabled={disabled} onClick={onClick}>
            {loading ? <div>Loading ...</div> : 
                <div>
                    {icon && iconPosition === 'left' && icon}
                    {children}
                    {icon && iconPosition === 'right' && icon}
                </div>
            }
        </button>
    )
}

export default Button