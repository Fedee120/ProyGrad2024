import './formStyles.scss'

const AddPropertyForm = ({errors, register, currencySymbol, setCurrencySymbol}: any) => {
    return (
        <>
            <div className='input-wrap'>
                <label htmlFor="name" className="label">Name</label>
                <input id="name" {...register('name', { required: true })} className="input" />
                {errors.name && <span className="text-red-500 text-xs">This field is required</span>}
            </div>
            <div className='input-wrap'>
                <label htmlFor="description" className="label">Description</label>
                <textarea id="description" {...register('description')} className="input h-fit max-h-[120px] min-h-[60px]" />
            </div>
            <div className="flex gap-3 flex-col md:flex-row">
                <div className='input-wrap'>
                    <label htmlFor="padron" className="label">Padron</label>
                    <input id="padron" {...register('padron')} className="input" />
                </div>
            </div>
            <div className='input-wrap'>
                <label htmlFor="addressString" className="label">Address</label>
                <input id="addressString" {...register('address.addressString', { required: true })} className="input" />
                {errors.address?.addressString && <span className="text-red-500 text-xs">This field is required</span>}
            </div>
            <div className="flex gap-3 flex-col md:flex-row">
                <div className='input-wrap'>
                    <label htmlFor="street" className="label">Street</label>
                    <input id="street" {...register('address.street', { required: true })} className="input" />
                    {errors.address?.street && <span className="text-red-500 text-xs">This field is required</span>}
                </div>
                <div className='input-wrap'>
                    <label htmlFor="streetNumber" className="label">Street Number</label>
                    <input id="streetNumber" {...register('address.streetNumber')} className="input" />
                </div>
            </div>
            <div className="flex gap-3 flex-col md:flex-row">
                <div className='input-wrap'>
                    <label htmlFor="city" className="label">City</label>
                    <input id="city" {...register('address.city', { required: true })} className="input" />
                    {errors.address?.city && <span className="text-red-500 text-xs">This field is required</span>}
                </div>
                <div className='input-wrap'>
                    <label htmlFor="department" className="label">Department</label>
                    <input id="department" {...register('address.department', { required: true })} className="input" />
                    {errors.address?.department && <span className="text-red-500 text-xs">This field is required</span>}
                </div>
            </div>
        </>
    )
}

export default AddPropertyForm