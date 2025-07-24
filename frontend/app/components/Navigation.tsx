
'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

export function Navigation() {
  const pathname = usePathname()

  const navItems = [
    { href: '/', label: 'Home' },
    { href: '/predict', label: 'Predict' },
    { href: '/batch', label: 'Batch' },
    { href: '/upload', label: 'Upload' },
    { href: '/model-info', label: 'Model Info' },
  ]

  return (
    <nav className="bg-cyber-dark/80 backdrop-blur-md border-b border-cyber-purple/20 sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link href="/" className="text-2xl font-bold glow-text">
            Airo
          </Link>
          
          <div className="hidden md:flex space-x-8">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`transition-all duration-300 hover:text-cyber-purple ${
                  pathname === item.href
                    ? 'text-cyber-purple border-b-2 border-cyber-purple'
                    : 'text-gray-300'
                }`}
              >
                {item.label}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </nav>
  )
}
