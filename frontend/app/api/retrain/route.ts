import { NextResponse } from 'next/server'

export async function POST() {
  try {
    const response = await fetch('http://localhost:8000/retrain', {
      method: 'POST',
    })

    if (!response.ok) {
      throw new Error('Backend request failed')
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to initiate retraining' },
      { status: 500 }
    )
  }
}
