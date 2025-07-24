import { NextResponse } from 'next/server'

export async function GET() {
  try {
    const response = await fetch('http://fastapi-backend:8000/model-info')

    if (!response.ok) {
      throw new Error('Backend request failed')
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.log(error)
    return NextResponse.json(
      { error: 'Failed to get model info ' },
      { status: 500 }
    )
  }
}
