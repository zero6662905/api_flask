from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import numpy as np
from multiprocessing import Pool
import time
from typing import List, Dict, Any, Optional
from math import factorial as math_factorial
from pydantic import BaseModel

app = FastAPI(docs_url="/")


# Модель для параметрів запиту
class CalculateParams(BaseModel):
    operation: str
    n: Optional[int] = None  # Для факторіалу
    range_end: Optional[int] = None  # Для простих чисел
    matrix_size: Optional[int] = None  # Для множення матриць
    array_size: Optional[int] = None  # Для статистики масиву


# Обмеження
MAX_FACTORIAL = 1000
MAX_PRIME_RANGE = 1_000_000
MAX_MATRIX_SIZE = 200
MAX_ARRAY_SIZE = 10_000_000
NUM_PROCESSES = 4  # Кількість процесів для великих завдань


# Функція для обчислення факторіалу
def compute_factorial(n: int) -> int:
    if n < 0 or n > MAX_FACTORIAL:
        raise ValueError(f"Factorial is supported for 0 <= n <= {MAX_FACTORIAL}")
    return math_factorial(n)


# Функція для знаходження простих чисел у діапазоні
def sieve_of_eratosthenes_chunk(start: int, end: int) -> List[int]:
    sieve = [True] * (end - start + 1)
    for i in range(2, int(end ** 0.5) + 1):
        for j in range(max(i * i, ((start + i - 1) // i) * i), end + 1, i):
            sieve[j - start] = False
    return [i + start for i in range(len(sieve)) if sieve[i] and (i + start) >= 2]


def compute_primes(range_end: int) -> List[int]:
    if range_end < 2 or range_end > MAX_PRIME_RANGE:
        raise ValueError(f"Prime range must be 2 <= range_end <= {MAX_PRIME_RANGE}")
    chunk_size = range_end // NUM_PROCESSES + 1
    chunks = [(i, min(i + chunk_size - 1, range_end)) for i in range(2, range_end + 1, chunk_size)]

    with Pool(NUM_PROCESSES) as pool:
        results = pool.starmap(sieve_of_eratosthenes_chunk, chunks)
    primes = []
    for chunk in results:
        primes.extend(chunk)
    return sorted(primes)


# Функція для множення матриць
def matrix_multiply(n: int) -> Dict[str, Any]:
    if n < 1 or n > MAX_MATRIX_SIZE:
        raise ValueError(f"Matrix size must be 1 <= n <= {MAX_MATRIX_SIZE}")
    A = np.random.randint(0, 10, size=(n, n))
    B = np.random.randint(0, 10, size=(n, n))
    C = np.dot(A, B)
    return {
        "matrix_A": A.tolist(),
        "matrix_B": B.tolist(),
        "result": C.tolist()
    }


# Функція для обчислення статистики масиву
def compute_array_stats_chunk(data: np.ndarray) -> Dict[str, float]:
    return {
        "mean": float(np.mean(data)),
        "median": float(np.median(data)),
        "std_dev": float(np.std(data))
    }


def compute_array_stats(array_size: int) -> Dict[str, float]:
    if array_size < 1 or array_size > MAX_ARRAY_SIZE:
        raise ValueError(f"Array size must be 1 <= size <= {MAX_ARRAY_SIZE}")
    data = np.random.randint(0, 100, size=array_size)
    chunk_size = array_size // NUM_PROCESSES + 1
    chunks = [data[i:i + chunk_size] for i in range(0, array_size, chunk_size)]

    with Pool(NUM_PROCESSES) as pool:
        results = pool.map(compute_array_stats_chunk, chunks)

    # Агрегація результатів
    means = [r["mean"] for r in results]
    medians = [r["median"] for r in results]
    std_devs = [r["std_dev"] for r in results]

    return {
        "mean": float(np.mean(means)),
        "median": float(np.median(medians)),
        "std_dev": float(np.mean(std_devs))
    }


@app.get("/calculate")
async def calculate(operation: str, n: Optional[int] = None, range_end: Optional[int] = None,
                    matrix_size: Optional[int] = None, array_size: Optional[int] = None):
    start_time = time.time()
    result = {}

    try:
        if operation == "factorial":
            if n is None:
                raise ValueError("Parameter 'n' is required for factorial")
            with Pool(1) as pool:
                result["factorial"] = pool.apply(compute_factorial, (n,))

        elif operation == "primes":
            if range_end is None:
                raise ValueError("Parameter 'range_end' is required for primes")
            result["primes"] = compute_primes(range_end)

        elif operation == "matrix_multiply":
            if matrix_size is None:
                raise ValueError("Parameter 'matrix_size' is required for matrix_multiply")
            with Pool(1) as pool:
                result["matrices"] = pool.apply(matrix_multiply, (matrix_size,))

        elif operation == "array_stats":
            if array_size is None:
                raise ValueError("Parameter 'array_size' is required for array_stats")
            result["statistics"] = compute_array_stats(array_size)

        else:
            raise ValueError("Invalid operation. Supported: factorial, primes, matrix_multiply, array_stats")

        result["execution_time_seconds"] = round(time.time() - start_time, 3)
        return JSONResponse(content=result)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(f"{__name__}:app", reload=True, port=5050)