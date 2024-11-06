Rails.application.routes.draw do
  root 'homepage#index'
  post 'homepage/get_info', to: 'homepage#get_info', as: 'homepage_get_info'

  get 'up' => 'rails/health#show', as: :rails_health_check
end
