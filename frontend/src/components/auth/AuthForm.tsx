import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { yupResolver } from '@hookform/resolvers/yup'
import * as yup from 'yup'
import { useAuth } from '../../contexts/AuthContext'
import './authStyles.scss'
import '../examples/forms/formStyles.scss'
import Button from '../common/Button/Button'
import { XmarkCircle } from 'iconoir-react'
import { toast } from 'react-toastify'
import Logo from '../../assets/logo.png'

const schema = yup.object().shape({
  email: yup.string().email('Invalid email format').required('Email is required'),
  password: yup.string().min(6, 'Password must be at least 6 characters').required('Password is required'),
})

const AuthForm = () => {
  const [error, setError] = useState<{ message: string }>({ message: '' })
  const { login } = useAuth()
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: yupResolver(schema)
  })
  const [loading, setLoading] = useState(false)
  
  const onSubmit = async (data: { email: string, password: string }) => {
    setLoading(true)
    try {
      await login(data.email, data.password)
      toast.success('Login successful')
    } catch (error: any) {
      setError({ message: 'Invalid credentials' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-container">
      <div className='flex align-center justify-center mb-6'><img src={Logo} alt='logo' className='ml-3' width={220} height={100} /></div>
      <form onSubmit={handleSubmit(onSubmit as any)} className="w-full form-container">
        <div className="flex flex-col gap-3 mb-3 text-center">
          <div className='text-4xl font-semibold leading-[140%]'>{error.message ? 'Oops...' : 'Welcome back!'}</div>
          {error.message && <p className='flex items-center px-3 py-2 bg-[#f8f8f8] rounded gap-2 text-red-500 text-[14px] font-medium leading-[160%]'><XmarkCircle width={20} height={20} color='#FF4444' />{error.message}</p>}
        </div>
        <div className='input-wrap'>
          <label htmlFor="email" className="label">Email</label>
          <input id="email" {...register('email')} type="email" className="input" placeholder='Email' />
          {errors.email && <span className="text-red-500 text-xs">{errors.email.message}</span>}
        </div>
        <div className='input-wrap'>
          <label htmlFor="password" className="label">Password</label>
          <input id="password" {...register('password')} type="password" className="input" placeholder='Password' />
          {errors.password && <span className="text-red-500 text-xs">{errors.password.message}</span>}
        </div>
        <div className='flex flex-col mt-6 gap-3'>
          <Button type='submit' loading={loading} size='large' disabled={loading}>
            Login
          </Button>
        </div>
      </form>
    </div>
  )
}

export default AuthForm