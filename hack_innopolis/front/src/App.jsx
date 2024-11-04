import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import {
	Card,
	CardContent,
	CardHeader,
	CardTitle,
	CardDescription,
} from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Trash2, Plus, RefreshCw, User, Users } from 'lucide-react';
import {
	ChartContainer,
	ChartTooltip,
	ChartTooltipContent,
} from '@/components/ui/chart';
import { Line, LineChart, XAxis, YAxis, ResponsiveContainer } from 'recharts';
import { Separator } from '@/components/ui/separator';

import { v4 as uuidv4 } from 'uuid';

import { Toaster } from '@/components/ui/toaster';
import { useToast } from '@/hooks/use-toast';

export default function App() {
	const { toast } = useToast();

	const [aspects, setAspects] = useState([]);
	const [newAspect, setNewAspect] = useState('');
	const [reviews, setReviews] = useState([]);
	const [aspectSummaries, setAspectSummaries] = useState([]);
	const [generalSummary, setGeneralSummary] = useState([]);
	const [selectedEmployeeId, setSelectedEmployeeId] = useState('');
	const [isLoading, setIsLoading] = useState(false);

	const [chartData, setChartData] = useState([]);

	const fetchAspects = async () => {
		try {
			const response = await fetch(`http://localhost:8000/reviews/api/aspects`);
			const data = await response.json();
			setAspects(data);
		} catch (error) {
			toast({
				title: 'Ошибка сервера!',
				description: 'Не удалось получить список аспектов.',
				variant: 'destructive',
			});
			console.error(error);
		}
	};

	const addAspect = async () => {
		if (newAspect) {
			try {
				await fetch(`http://localhost:8000/reviews/api/aspects`, {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json',
					},
					body: JSON.stringify({
						text: newAspect,
					}),
				});
				setNewAspect('');
				await toast({
					title: 'Аспект добавлен!',
					description: 'Аспект был успешно добавлен.',
				});
				await fetchAspects();
			} catch (error) {
				toast({
					title: 'Ошибка сервера!',
					description: 'Не удалось добавить аспект.',
					variant: 'destructive',
				});
				setNewAspect('');
				console.error(error);
			}
		}
	};

	const deleteAspect = async (id) => {
		try {
			await fetch(`http://localhost:8000/reviews/api/aspects/${id}`, {
				method: 'DELETE',
			});
			await toast({
				title: 'Аспект удален!',
				description: 'Аспект был успешно удален.',
			});
			await fetchAspects();
		} catch (error) {
			toast({
				title: 'Ошибка сервера!',
				description: 'Не удалось удалить аспект.',
				variant: 'destructive',
			});
			console.log(error);
		}
	};

	const isFetchError = (response, status, message) => {
		if (response.status === status) {
			toast({
				title: status,
				description: message,
				variant: 'destructive',
			});
			return true;
		}
	};

	const fetchReviews = async (employeeId) => {
		try {
			const response = await fetch(
				`http://localhost:8000/reviews/api/feedback/${employeeId}`
			);
			if (isFetchError(response, 404, 'Сотрудник не найден')) {
				return;
			}
			const data = await response.json();
			if (data.length === 0) {
				toast({
					title: 'Отзывы отсутствуют!',
					description: 'Сотруднику ещё не оставляли отзывы.',
					variant: 'destructive',
				});
				return;
			}
			setReviews(data);
			console.log(data);
		} catch (error) {
			toast({
				title: 'Ошибка сервера!',
				description: 'Не удалось получить отзывы на сотрудника.',
				variant: 'destructive',
			});
			console.log(error);
		}
	};

	const fetchAspectSummary = async (employeeId) => {
		try {
			const response = await fetch(
				`http://localhost:8000/reviews/api/aspect-summaries/${employeeId}`
			);
			if (isFetchError(response, 404, 'Сотрудник не найден')) {
				return;
			}
			const data = await response.json();
			if (data.length === 0) {
				toast({
					title: 'Анализы компетенции отсутствуют!',
					description: 'Анализ сотрудника еще не проводился.',
					variant: 'destructive',
				});
				return;
			}
			setAspectSummaries(data);
			console.log(data);
		} catch (error) {
			toast({
				title: 'Ошибка сервера!',
				description: 'Не удалось получить анализ по аспектам сотрудника.',
				variant: 'destructive',
			});
			console.log(error);
		}
	};

	const fetchGeneralSummary = async (employeeId) => {
		try {
			const response = await fetch(
				`http://localhost:8000/reviews/api/general-summaries/${employeeId}`
			);
			if (isFetchError(response, 404, 'Сотрудник не найден')) {
				return;
			}
			const data = await response.json();
			if (data.length === 0) {
				toast({
					title: 'Анализы компетенции отсутствуют!',
					description: 'Анализ сотрудника еще не проводился.',
					variant: 'destructive',
				});
				return;
			}

			const chartData = data.map((item, index) => {
				return { index, score: item.score };
			});
			setChartData(chartData);

			const newGeneralSummary = data.reverse();
			setGeneralSummary(newGeneralSummary);
			console.log(newGeneralSummary);
		} catch (error) {
			toast({
				title: 'Ошибка сервера!',
				description: 'Не удалось получить итоговый анализ сотрудника.',
				variant: 'destructive',
			});
			console.log(error);
		}
	};

	const fetchEmployeeData = async (employeeId) => {
		try {
			setIsLoading(true);
			fetchReviews(employeeId);
			fetchAspectSummary(employeeId);
			fetchGeneralSummary(employeeId);
			toast({
				title: 'Данные сотрудника загружены!',
				description:
					'Данные сотрудника были успешно загружены. Перейдите в раздел "Отзывы" для просмотра отзывов и в раздел "Анализы" для просмотра анализов.',
			});
			setIsLoading(false);
		} catch (error) {
			toast({
				title: 'Ошибка сервера!',
				description: 'Не удалось получить данные сотрудника.',
				variant: 'destructive',
			});
			console.log(error);
		}
	};

	const generateAnalysis = async () => {
		try {
			setIsLoading(true);
			await fetch(
				`http://localhost:8000/reviews/api/feedback/generate-summary/${selectedEmployeeId}`,
				{
					method: 'POST',
				}
			);
			toast({
				title: 'Анализ сотрудника обновлен!',
				description: 'Анализ сотрудника был успешно обновлен.',
			});
			await fetchEmployeeData(selectedEmployeeId);
			toast({
				title: 'Получены новые данные!',
				description:
					'Новые данные были успешно получены. Перейдите в раздел "Отзывы" для просмотра отзывов и в раздел "Анализы" для просмотра анализов.',
			});
		} catch (error) {
			toast({
				title: 'Ошибка сервера!',
				description: 'Не удалось обновить анализ сотрудника.',
				variant: 'destructive',
			});
			console.log(error);
		}

		setIsLoading(false);
	};

	useEffect(() => {
		fetchAspects();
	}, []);

	return (
		<>
			<div className='space-y-4 mx-auto p-4 container'>
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

				<Tabs defaultValue='aspects' className='space-y-4'>
					<TabsList>
						<TabsTrigger value='aspects'>Аспекты анализа</TabsTrigger>
						<TabsTrigger disabled={reviews.length === 0} value='reviews'>
							Отзывы
						</TabsTrigger>
						<TabsTrigger
							disabled={
								generalSummary.length === 0 || aspectSummaries.length === 0
							}
							value='summary'
						>
							Общий анализ
						</TabsTrigger>
					</TabsList>

					<TabsContent value='aspects'>
						<Card>
							<CardHeader>
								<CardTitle>Управление аспектами</CardTitle>
								<CardDescription>
									Добавляйте или удаляйте аспекты для анализа сотрудников
								</CardDescription>
							</CardHeader>
							<CardContent>
								<div className='flex gap-2 mb-4'>
									<Input
										placeholder='Новый аспект'
										value={newAspect}
										onChange={(e) => setNewAspect(e.target.value)}
									/>
									<Button onClick={addAspect} disabled={!newAspect}>
										<Plus className='mr-2 w-4 h-4' />
										Добавить
									</Button>
								</div>
								<ScrollArea className='w-full h-[400px]'>
									<div className='space-y-2'>
										{aspects.map((aspect) => (
											<div
												key={aspect.id}
												className='flex justify-between items-center p-2 border rounded'
											>
												<span className='pl-2'>{aspect.text}</span>
												<Button
													variant='ghost'
													size='icon'
													onClick={() => deleteAspect(aspect.id)}
												>
													<Trash2 className='w-4 h-4' />
													<span className='sr-only'>Удалить аспект</span>
												</Button>
											</div>
										))}
									</div>
								</ScrollArea>
							</CardContent>
						</Card>
					</TabsContent>

					<TabsContent value='reviews'>
						<Card>
							<CardHeader>
								<CardTitle>Отзывы о сотруднике</CardTitle>
								<CardDescription>
									Просмотр всех отзывов о выбранном сотруднике
								</CardDescription>
							</CardHeader>
							<CardContent>
								<ScrollArea className='h-[500px]'>
									<div className='space-y-4'>
										{reviews &&
											reviews.map((review) => (
												<Card key={uuidv4()}>
													<CardContent className='pt-6'>
														<div className='flex justify-between items-start mb-2'>
															<div className='flex items-center gap-2'>
																{review.is_self_review ? (
																	<User className='w-5 h-5 text-blue-500' />
																) : (
																	<Users className='w-5 h-5 text-green-500' />
																)}
																<Badge
																	variant={
																		review.is_self_review
																			? 'secondary'
																			: 'default'
																	}
																>
																	{review.is_self_review
																		? 'Самооценка'
																		: 'Оценка коллеги'}
																</Badge>
															</div>
														</div>
														<p className='mb-2 text-sm'>{review.review}</p>
														<Separator className='my-2' />
														<div className='text-muted-foreground text-xs'>
															ID рецензента: {review.ID_reviewer}
														</div>
													</CardContent>
												</Card>
											))}
									</div>
								</ScrollArea>
							</CardContent>
						</Card>
					</TabsContent>

					<TabsContent value='summary'>
						<div className='gap-4 grid'>
							<div className='gap-4 grid grid-cols-2'>
								<Card>
									<CardHeader>
										<CardTitle>История общих сводок</CardTitle>
										<CardDescription>
											Итоговые оценки и общее описание сотрудника
										</CardDescription>
									</CardHeader>
									<CardContent>
										<ScrollArea className='h-[500px]'>
											{generalSummary &&
												generalSummary.map((summary) => (
													<Card className='mb-4 pt-4' key={uuidv4()}>
														<CardContent>
															<div className='space-y-4'>
																<div className='flex justify-between items-center'>
																	<div className='font-bold text-3xl'>
																		{summary.score?.toFixed(1)} / 5
																	</div>
																	<Badge
																		variant='secondary'
																		className='px-3 py-1 text-lg'
																	>
																		Общая оценка
																	</Badge>
																</div>
																<p className='text-sm'>{summary.text}</p>
																<div className='text-muted-foreground text-xs'>
																	Обновлено:{' '}
																	{new Date(
																		summary.created_at
																	).toLocaleString()}
																</div>
															</div>
														</CardContent>
													</Card>
												))}
										</ScrollArea>
									</CardContent>
								</Card>

								<Card>
									<CardHeader>
										<CardTitle>Анализ по аспектам</CardTitle>
										<CardDescription>
											Детальный разбор по каждому аспекту оценки
										</CardDescription>
									</CardHeader>
									<CardContent>
										<ScrollArea className='h-[500px]'>
											<div className='gap-4 grid'>
												{aspectSummaries &&
													aspectSummaries.reverse().map((summary) => (
														<Card key={uuidv4()}>
															<CardContent className='pt-6'>
																<div className='flex justify-between items-center mb-2'>
																	<h4 className='font-semibold text-lg'>
																		{summary.aspect_name}
																	</h4>
																	<Badge
																		variant='secondary'
																		className='px-3 py-1 text-lg'
																	>
																		{summary.score.toFixed(1)} / 5
																	</Badge>
																</div>
																<p className='mb-2 text-sm'>{summary.text}</p>
																<div className='text-muted-foreground text-xs'>
																	Обновлено:{' '}
																	{new Date(
																		summary.created_at
																	).toLocaleString()}
																</div>
															</CardContent>
														</Card>
													))}
											</div>
										</ScrollArea>
									</CardContent>
								</Card>
							</div>

							{chartData.length > 1 && (
								<Card>
									<CardHeader>
										<CardTitle>Динамика оценок</CardTitle>
										<CardDescription>
											График изменения общей оценки
										</CardDescription>
									</CardHeader>
									<CardContent>
										<div>
											<ChartContainer
												config={{
													score: {
														label: 'Оценка',
														color: 'hsl(var(--chart-1))',
													},
												}}
												className='w-full h-[300px]'
											>
												<ResponsiveContainer width='100%' height='20%'>
													<LineChart data={chartData}>
														<XAxis
															dataKey='index'
															tickLine={false}
															axisLine={false}
														/>
														<YAxis
															tickLine={false}
															axisLine={false}
															tickFormatter={(value) => `${value.toFixed(1)}`}
															domain={[0, 5]}
														/>
														<Line
															type='monotone'
															dataKey='score'
															strokeWidth={2}
															activeDot={{ r: 8 }}
														/>
														<ChartTooltip content={<ChartTooltipContent />} />
													</LineChart>
												</ResponsiveContainer>
											</ChartContainer>
										</div>
									</CardContent>
								</Card>
							)}
						</div>
					</TabsContent>
				</Tabs>
			</div>
			<Toaster />
		</>
	);
}
