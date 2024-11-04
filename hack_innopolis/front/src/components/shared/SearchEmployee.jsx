const SearchEmployee = () => {
	return (
		<div className='flex sm:flex-row flex-col items-center gap-4 mb-6'>
			<Input
				type='number'
				placeholder='ID сотрудника'
				value={selectedEmployeeId}
				onChange={(e) => setSelectedEmployeeId(Number(e.target.value))}
				className='max-w-xs'
			/>
			<Button
				onClick={() => fetchEmployeeData(selectedEmployeeId)}
				disabled={!selectedEmployeeId || isLoading}
			>
				Загрузить данные
			</Button>
			<Button
				onClick={generateAnalysis}
				disabled={!selectedEmployeeId || isLoading}
				variant='secondary'
			>
				<RefreshCw className='mr-2 w-4 h-4' />
				Произвести / обновить анализ
			</Button>
		</div>
	);
};

export default SearchEmployee;
